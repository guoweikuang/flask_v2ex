.. _crawler:


爬虫相关
========================================


基于Tornado的异步爬虫
___________________________________

.. code-block:: python

    #!/usr/bin/env python
    # -*- coding:utf-8 -*-

    import time
    import logging
    from datetime import timedelta
    from tornado import httpclient, gen, ioloop, queues
    import traceback
    from bs4 import BeautifulSoup


    def logged(class_):
        logging.basicConfig(level=logging.INFO)
        class_.logger = logging.getLogger(class_.__name__)
        return class_


    @logged
    class AsyncSpider(object):
        """A simple class of asynchronous spider."""
        def __init__(self, urls, concurrency=10, results=None, **kwargs):
            super(AsyncSpider, self).__init__(**kwargs)

            self.concurrency = concurrency
            self._q = queues.Queue()
            self._fetching = set()
            self._fetched = set()
            if results is None:
                self.results = []
            for url in urls:
                self._q.put(url)
            httpclient.AsyncHTTPClient.configure(
                "tornado.curl_httpclient.CurlAsyncHTTPClient"
            )

        def fetch(self, url, **kwargs):
            fetch = getattr(httpclient.AsyncHTTPClient(), 'fetch')
            http_request = httpclient.HTTPRequest(url, **kwargs)
            return fetch(http_request, raise_error=False)

        def handle_html(self, url, html):
            """处理html页面"""
            print(url)

        def handle_response(self, url, response):
            """处理http响应，对于200响应码直接处理html页面，
            否则按照需求处理不同响应码"""
            if response.code == 200:
                self.handle_html(url, response.body)

            elif response.code == 599:    # retry
                self._fetching.remove(url)
                self._q.put(url)

        @gen.coroutine
        def get_page(self, url):
            # yield gen.sleep(10)    # sleep when need
            try:
                response = yield self.fetch(url)
                self.logger.debug('######fetched %s' % url)
            except Exception as e:
                self.logger.debug('Exception: %s %s' % (e, url))
                raise gen.Return(e)
            raise gen.Return(response)    # py3 can just return response

        @gen.coroutine
        def _run(self):
            @gen.coroutine
            def fetch_url():
                current_url = yield self._q.get()
                try:
                    if current_url in self._fetching:
                        return

                    self.logger.debug('fetching****** %s' % current_url)
                    self._fetching.add(current_url)

                    response = yield self.get_page(current_url)
                    self.handle_response(current_url, response)    # handle reponse

                    self._fetched.add(current_url)

                finally:
                    self._q.task_done()

            @gen.coroutine
            def worker():
                while True:
                    yield fetch_url()

            # Start workers, then wait for the work queue to be empty.
            for _ in range(self.concurrency):
                worker()

            yield self._q.join(timeout=timedelta(seconds=300000))

            try:
                assert self._fetching == self._fetched
            except AssertionError:    # some http error not handle
                print(self._fetching-self._fetched)
                print(self._fetched-self._fetching)

        def run(self):
            io_loop = ioloop.IOLoop.current()
            io_loop.run_sync(self._run)


    class MySpider(AsyncSpider):

        def fetch(self, url, **kwargs):
            """重写父类fetch方法可以添加cookies，headers，timeout等信息"""
            cookies_str = "PHPSESSID=j1tt66a829idnms56ppb70jri4; pspt=%7B%22id%22%3A%2233153%22%2C%22pswd%22%3A%228835d2c1351d221b4ab016fbf9e8253f%22%2C%22_code%22%3A%22f779dcd011f4e2581c716d1e1b945861%22%7D; key=%E9%87%8D%E5%BA%86%E5%95%84%E6%9C%A8%E9%B8%9F%E7%BD%91%E7%BB%9C%E7%A7%91%E6%8A%80%E6%9C%89%E9%99%90%E5%85%AC%E5%8F%B8; think_language=zh-cn; SERVERID=a66d7d08fa1c8b2e37dbdc6ffff82d9e|1444973193|1444967835; CNZZDATA1254842228=1433864393-1442810831-%7C1444972138"
            headers = {
                'User-Agent': 'mozilla/5.0 (compatible; baiduspider/2.0; +http://www.baidu.com/search/spider.html)',
                'cookie': cookies_str
            }
            return super(MySpider, self).fetch(
                url, headers=headers,
                #proxy_host="127.0.0.1", proxy_port=8787,    # for proxy
            )

        def handle_html(self, url, html):
            print(url)
            #print(BeautifulSoup(html, 'lxml').find('title'))


    def main():
        st = time.time()
        urls = []
        n = 1000
        for page in range(1, n):
            urls.append('http://www.jb51.net/article/%s.htm' % page)
        s = MySpider(urls, 10)
        s.run()
        print(time.time()-st)
        print(60.0/(time.time()-st)*1000, 'per minute')
        print(60.0/(time.time()-st)*1000/60.0, 'per second')


    if __name__ == '__main__':
        main()



写爬虫会遇到的一些工具函数
___________________________________

.. code-block:: python

    #!/usr/bin/env python
    # -*- coding:utf-8 -*-

    """
    chrome有个功能，对于请求可以直接右键copy as curl，然后在命令行里边用curl
    模拟发送请求。现在需要把此curl字符串处理成requests库可以传入的参数格式，
    http://stackoverflow.com/questions/23118249/whats-the-difference-between-request-payload-vs-form-data-as-seen-in-chrome
    """

    import re
    from functools import wraps
    import traceback
    import requests


    def encode_to_dict(encoded_str):
        """ 将encode后的数据拆成dict
        >>> encode_to_dict('name=foo')
        {'name': foo'}
        >>> encode_to_dict('name=foo&val=bar')
        {'name': 'foo', 'val': 'var'}
        """

        pair_list = encoded_str.split('&')
        d = {}
        for pair in pair_list:
            if pair:
                key = pair.split('=')[0]
                val = pair.split('=')[1]
                d[key] = val
        return d


    def parse_curl_str(s):
        """convert chrome curl string to url, headers_dict and data"""
        pat = re.compile("'(.*?)'")
        str_list = [i.strip() for i in re.split(pat, s)]   # 拆分curl请求字符串

        url = ''
        headers_dict = {}
        data = ''

        for i in range(0, len(str_list)-1, 2):
            arg = str_list[i]
            string = str_list[i+1]

            if arg.startswith('curl'):
                url = string

            elif arg.startswith('-H'):
                header_key = string.split(':', 1)[0].strip()
                header_val = string.split(':', 1)[1].strip()
                headers_dict[header_key] = header_val

            elif arg.startswith('--data'):
                data = string

        return url, headers_dict, data


    def retry(retries=3):
        """一个失败请求重试，或者使用下边这个功能强大的retrying
        pip install retrying
        https://github.com/rholder/retrying

        :param retries: number int of retry times.
        """
        def _retry(func):
            @wraps(func)
            def _wrapper(*args, **kwargs):
                index = 0
                while index < retries:
                    index += 1
                    try:
                        response = func(*args, **kwargs)
                        if response.status_code == 404:
                            print(404)
                            break
                        elif response.status_code != 200:
                            print(response.status_code)
                            continue
                        else:
                            break
                    except Exception as e:
                        traceback.print_exc()
                        response = None
                return response
            return _wrapper
        return _retry


    _get = requests.get


    @retry(5)
    def get(*args, **kwds):
        if 'timeout' not in kwds:
            kwds['timeout'] = 10
        if 'headers' not in kwds:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36',
            }
            kwds['headers'] = headers

        return _get(*args, **kwds)

    requests.get = get


    def retry_get_html(*args, **kwargs):
        try:
            return get(*args, **kwargs).content
        except AttributeError:
            return ''


    def lazy_property(fn):
        attr_name = '_lazy_' + fn.__name__

        @property
        def _lazy_property(self):
            if not hasattr(self, attr_name):
                setattr(self, attr_name, fn(self))
                return getattr(self, attr_name)
        return _lazy_property


    def my_ip():
        # url = 'https://api.ipify.org?format=json'
        url = 'http://httpbin.org/ip'
        return requests.get(url).text


    def form_data_to_dict(s):
        """form_data_to_dict s是从chrome里边复制得到的form-data表单里的字符串，
        注意*必须*用原始字符串r""

        :param s: form-data string
        """
        arg_list = [line.strip() for line in s.split('\n')]
        d = {}
        for i in arg_list:
            if i:
                k = i.split(':', 1)[0].strip()
                v = ''.join(i.split(':', 1)[1:]).strip()
                d[k] = v
        return d

    if __name__ == '__main__':
        import sys
        from pprint import pprint
        try:
            curl_str = sys.argv[1]   # 用三引号括起来作为参数
            url, headers_dict, data = parse_curl_str(curl_str)
            print(url)
            pprint(headers_dict)
            print(data)
        except IndexError:
            exit(0)


如何使用代理
___________________

.. code-block:: python

    #!/usr/bin/env python
    # -*- coding:utf-8 -*-

    # requests proxy demo
    import requests

    # install lantern first, 这是使用lantern的代理地址
    proxies = {
        "http": "http://127.0.0.1:8787",
        "https": "http://127.0.0.1:8787",
    }

    url = 'http://httpbin.org/ip'
    r = requests.get(url, proxies=proxies)
    print(r.text)


    # requests from version 2.10.0 support socks proxy
    # pip install -U requests[socks]
    proxies = {'http': "socks5://myproxy:9191"}
    requests.get('http://example.org', proxies=proxies)

    # tornado proxy demo
    # sudo apt-get install libcurl-dev librtmp-dev
    # pip install tornado pycurl

    from tornado import httpclient, ioloop

    config = {
        'proxy_host': 'YOUR_PROXY_HOSTNAME_OR_IP_ADDRESS',
        'proxy_port': 3128
    }

    httpclient.AsyncHTTPClient.configure(
        "tornado.curl_httpclient.CurlAsyncHTTPClient")


    def handle_request(response):
        if response.error:
            print "Error:", response.error
        else:
            print response.body
        ioloop.IOLoop.instance().stop()

    http_client = httpclient.AsyncHTTPClient()
    http_client.fetch("http://twitter.com/",
        handle_request, **config)
    ioloop.IOLoop.instance().start()


使用线程池
_______________

.. code-block:: python

 #!/usr/bin/env python
 # -*- coding:utf-8 -*-
 import concurrent.futures
 import bs4
 import requests


 class ThreadPoolCrawler(object):
     def __init__(self, urls, concurrency=10, **kwargs):
         self.urls = urls
         self.concurrency = concurrency
         self.results = []

     def handle_response(self, url, response):
         pass

     def get(self, *args, **kwargs):
         return requests.get(*args, **kwargs)

     def run(self):
         with concurrent.futures.ThreadPoolExecutor(max_workers=self.concurrency) as executor:
             future_to_url = {
                 executor.submit(self.get, url): url for url in self.urls
             }
             for future in concurrent.futures.as_completed(future_to_url):
                 url = future_to_url[future]
                 try:
                     response = future.result()
                 except Exception as e:
                     import traceback
                     traceback.print_exc()
                 else:
                     self.handle_response(url, response)


 class TestCrawler(ThreadPoolCrawler):
     def handle_response(self, url, response):
         soup = bs4.BeautifulSoup(response.text, 'lxml')
         title = soup.find('title')
         self.results.append({url: title})


 def main():
     import time
     urls = ['http://localhost:8000'] * 300
     for nums in [2, 5, 10, 15, 20, 50, 70, 100]:
         beg = time.time()
         s = TestCrawler(urls, nums)
         s.run()
         print(nums, time.time()-beg)

 if __name__ == '__main__':
     main()



使用tor代理ip
__________________

.. code-block:: python

    #!/usr/bin/env python
    # -*- coding:utf-8 -*-

	# http://ningning.today/2016/03/07/python/python-requests-tor-crawler/

    import os
    import requests
    import requesocks

    #url = 'https://api.ipify.org?format=json'
    url = 'http://httpbin.org/ip'


    def getip_requests(url):
        print "(+) Sending request with plain requests..."
        r = requests.get(url)
        print "(+) IP is: " + r.text.replace("\n", "")


    def getip_requesocks(url):
        print "(+) Sending request with requesocks..."
        session = requesocks.session()
        session.proxies = {'http': 'socks5://127.0.0.1:9050',
                           'https': 'socks5://127.0.0.1:9050'}
        r = session.get(url)
        print "(+) IP is: " + r.text.replace("\n", "")


    def tor_requests():
        proxies = {
            'http': 'socks5://127.0.0.1:9050',
            'https': 'socks5://127.0.0.1:9050',
        }
        r = requests.get(url, proxies=proxies)
        print r.text


    def main():
        print "Running tests..."
        getip_requests(url)
        getip_requesocks(url)
        os.system("""(echo authenticate '"yourpassword"'; echo signal newnym; echo quit) | nc localhost 9051""")
        getip_requesocks(url)


    if __name__ == "__main__":
        main()
        #tor_requests()


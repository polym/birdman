import re
import os
from upyun import UpYun

def listdir(up, bucket, path):
    pinfo = up.getlist(path)
    data = '<title>Directory listing for %s</title><body>' % path
    data += '<h2>Directory listing for %s</h2><hr><ul>' % path
    for f in pinfo:
        if f['type'] == 'N':
            data += '<li><a href="http://%s.b0.upaiyun.com%s%s">%s</a>' % \
                    (bucket, path, f['name'], f['name'])
        else:
            data += '<li><a href="list.html?dir=/%s%s%s/">%s/</a>' % \
                    (bucket, path, f['name'], f['name'])
    data += '</ul><hr></body></html>'
    return str(data)
    

def app(environ, start_response):
    path = environ['PATH_INFO']
    data = ''
    if path == "/list.html":
        query = environ['QUERY_STRING']
        print query
        m = re.match(r'^dir=/([^/]*)(.*)', query)
        bucket, fpath = m.group(1), m.group(2)

        up = UpYun(bucket = bucket, username = 'myworker',
                password = 'tyghbnTYGHBN'
            )

        info = up.getinfo(key = fpath)
        if info['file-type'] == 'folder':
            # TODO add folder list to html
            status = '200 OK'
            data = listdir(up, bucket, fpath)
            start_response(status, [
                ("Content-Type", "text/html"),
                ("Content-Length", str(len(data)))
            ])
        else:
            status = '302 Temporarily Moved'
            start_response(status, [
                ("Content-Type", "text/plain"),
                ("Content-Length", str(len(data)))
                (
                    "Location", "http://%s.b0.upaiyun.com%s" % 
                    (bucket, fpath)
                ),
            ])
    elif path == "/upload.html":
        pass

    return iter([data])

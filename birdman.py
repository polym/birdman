import re
import os
import time
import config
import requests
from upyun import UpYun

def fsize2str(fsize, bar):
    if fsize == -1:
        return '-'
    res = '%d' % fsize
    if fsize >= 10**bar:
        fsize /= 1024
        res = '%dK' % fsize
        if fsize >= 10 ** (bar-1):
            fsize /= 1024
            res = '%dM' % fsize
            if fsize >= 10 ** (bar-1):
                fsize /= 1024
                res = '%dG' % fsize
    return res

def addrow(href, fname, ftime, fsize = -1):
    html = '<a href="%s">%s</a>' % (href, fname)
    fsize = int(fsize)
    fz = fsize2str(fsize, 4)
    ft = time.strftime("%d-%b-%Y %H:%M", time.localtime(int(ftime)))
    bar = 76 - len(fname)
    s = '%+17s\t%+4s' % (ft, fz)
    html += ' ' * (bar - 25) + s + '\n'
    return html
    

def listdir(up, bucket, path):
    pinfo = up.getlist(path)
    sinfo = sorted(pinfo, key = lambda k: "%s %s" % (k['type'], k['time']))
    
    data = '<title>Directory listing for %s</title><body>' % path
    data += '<h2>Directory listing for %s</h2><hr><pre>' % path
    if path != '/':
        father = '/'.join(path.split('/')[:-2])
        data += '<a href="list.html?dir=/%s%s/">../</a>\n' % (bucket, father)
    for f in sinfo:
        if f['type'] == 'N':
            href = 'http://%s.b0.upaiyun.com%s%s' % (bucket, path, f['name'])
            data += addrow(href, f['name'], f['time'], f['size'])
        else:
            href = 'list.html?dir=/%s%s%s/' % (bucket, path, f['name'])
            data += addrow(href, f['name']+'/', f['time'], '-1')
    data += '</pre><hr></body></html>'
    return str(data)
    

def app(environ, start_response):
    path = environ['PATH_INFO']
    data = ''
    if path == "/list.html":
        query = environ['QUERY_STRING']
        m = re.match(r'^dir=/([^/]*)(.*)', query)
        bucket, fpath = m.group(1), m.group(2)

        up = UpYun(bucket = bucket, username = config.username, 
                password = config.password
            )

        info = up.getinfo(key = fpath)
        if info['file-type'] == 'folder':
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
        m = re.match(r'uri=(.*)&dir=/([^/]*)(.*)', environ['QUERY_STRING'])
        uri, bucket, fpath = m.group(1), m.group(2), m.group(3)
        blob = ''
        resp = requests.get(uri, stream=True, timeout=5)
        for chunk in resp.iter_content(8192):
            if not chunk:
                break
            blob += chunk
        if blob != '':
            up = UpYun(bucket = bucket, username = config.username, 
                    password = config.password
                )
            up.put(fpath, blob)
        data = '%s Upload to /%s%s .. OK' % (uri, bucket, fpath)

    else:
        status = '200 OK'
        data += '<h1>usage</h1>\n'
        data += '<p>/list.html?dir=</bucket/path/to/file></p>\n'
        data += '<p>/post.html?uri=<uri>&&dir=</bucket/path/to/file></p>\n'
        start_response(status, [
            ("Content-Type", "text/html"),
            ("Content-Length", str(len(data)))
        ])

    return iter([data])


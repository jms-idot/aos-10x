from functools import partial
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import sys
from tenx_utils import sanitize_field
from urllib.parse import urlparse

"""
A simple HTTP server to handle requests to query the contents of the
csv data.  The constructor will take in the relevant arguments for 
responding to requests.
"""
class TenXHttpHandler(BaseHTTPRequestHandler):
    def __init__(self, data, *args, **kwargs):
        self.data = data
        self.limit = -1

        # BaseHTTPRequestHandler calls do_GET **inside** __init__ !!!
        # So we have to call super().__init__ after setting attributes.
        super().__init__(*args, **kwargs)

    """
    Checks query filters, for now only the operators: <, <=, >, >=, and = 
    are supported.  Numeric types are required for queries other than =.
    Range queries are not supported.  None is returned in case of an error.
    """
    def apply_filter(self, filter, data):
        # need at least one row of data in order to operate
        if len(data) < 1:
            return data

        # get labels
        labels = data[0].keys()

        # generator operators in order of largest to smallest
        operators = [ '<=', '>=', '<', '>', '=' ]
        operators.sort(reverse=True, key=len)

        for operator in operators:
            f = filter.split(operator)
            if len(f) == 1:
                # check next operators
                continue
            elif len(f) == 2:
                # process the operator
                break
            else:
                # the filter should be of the form: <field><operator><value>, thus
                # an error in the filter specified.  return None to indicate error
                return None
        if len(f) != 2:
            # No operator was found, return None to indicate an error
            return None

        # perform filtering
        field = f[0]
        value = sanitize_field(f[1])

        # verify field is known field
        if not field in labels:
            return None
        
        # if operator is something other than '=', the value must be numeric
        if operator != '=' and not (isinstance(value, int) or isinstance(value, float)):
            return None
            
        # apply query
        result = []
        if operator == '<=':
            result = [d for d in data if d[field] <= value]
        elif operator == '>=':
            result = [d for d in data if d[field] >= value]
        elif operator == '<':
            result = [d for d in data if d[field] < value]
        elif operator == '>':
            result = [d for d in data if d[field] > value]
        elif operator == '=':
            result = [d for d in data if d[field] == value]

        return result

    def set_error_response(self, message, code):
        print(message)
        print(type(message))
        print('Error: ' + message, file=sys.stderr)
        self.send_response(code)
        self.end_headers()

    def do_GET(self):
        # set limit to all
        limit = -1

        # get the path components
        path = [p for p in os.path.split(self.path[1:]) if len(p) > 0]
        if not path:
            # we have a general get request, send all the data as json
            self.send_response(200)
            self.send_header('Content-type','application/json')
            self.end_headers()

            # write the data
            self.wfile.write(json.dumps(self.data).encode("utf-8"))
        elif len(path) != 1 or not path[0].startswith("query"):
            # the only allowed operation is 'query', so if we have multiple possible
            # commands or something other than query, return 400
            self.set_error_response('only "query" operation allowed', 400)
            return
        else:
            # are the fields requested to be queried valid? if not, return 400
            # query?wind>=5.1&date
            query = urlparse(self.path).query
            query_compents = query.split("&")
            tmp_data = self.data
            for c in query_compents:
                # do we have a limit line?  multiple limit lines will use
                # the last limit specified
                print(c)
                if c.startswith("limit"):
                    lc = c.split("=")
                    if len(lc) != 2:
                        # limit needs to be of the form limit=<value>
                        self.set_error_respone('limit needs to be of the form "limit=<int value>"', 400)
                        return
                    else:
                        limit = sanitize_field(lc[1])
                        if not isinstance(limit, int):
                            self.set_error_respone('limit needs to be integer', 400)
                            return
                else:
                    tmp_data = self.apply_filter(c, tmp_data)
                    if tmp_data == None:
                        self.set_error_response('error applying filter - ' + c, 400)
                        return
            # send the result, could be empty!
            self.send_response(200)
            self.send_header('Content-type','application/json')
            self.end_headers()
            if limit != -1:
                tmp_data = tmp_data[:limit]
            self.wfile.write(json.dumps(tmp_data).encode("utf-8"))

def launch_server(port, data):
    tenX_handler = partial(TenXHttpHandler, data)
    server = HTTPServer(('', port), tenX_handler)
    print("server listening on port -", port)
    server.serve_forever()
import os.path
import wordclouds
from flask import Flask, Response, url_for, send_file, request, jsonify


app = Flask(__name__)
app.config.from_object(__name__)


def get_file(filename):  # pragma: no cover
    try:
        src = os.path.join(root_dir(), filename)
        # Figure out how flask returns static files
        # Tried:
        # - render_template
        # - send_file
        # This should not be so non-obvious
        return open(src).read()
    except IOError as exc:
        return str(exc)

def root_dir():  # pragma: no cover
    return os.path.abspath(os.path.dirname("../frontend/"))




@app.route('/', methods=['GET'])
def index():
    content = get_file('index.html')
    return Response(content, mimetype="text/html")


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def get_resource(path):  # pragma: no cover
    mimetypes = {
        ".css": "text/css",
        ".html": "text/html",
        ".js": "application/javascript",
    }
    complete_path = os.path.join(root_dir(), path)
    ext = os.path.splitext(path)[1]
    mimetype = mimetypes.get(ext, "text/html")
    content = get_file(complete_path)
    return Response(content, mimetype=mimetype)



@app.route('/db', methods=['GET'])
def db():
	return send_file(os.path.join(root_dir(),'example.db'))
	#content = get_file('../frontend/example.db')
	#return Response(content)





@app.route("/ptagcloudapi", methods=['GET', 'POST'])
def hello():
	print("something")
	print(request.json)
	wc = wordclouds.getCorpusJSON(request.json)
	print("Corpus Retrieved")
	fd = wordclouds.getWordCloudWords(wc)
	print("Words Counted")
	print(fd)
	return jsonify(fd)








if __name__ == '__main__':  # pragma: no cover
    app.run()
translations:
	echo "Run source venv/bin/activate first"
	django-admin makemessages -l de -e txt,html,subject,py

graph:
	dot -Tsvg -o eventFlow.svg eventFlow.dot

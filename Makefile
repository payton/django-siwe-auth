test:
	DJANGO_SETTINGS_MODULE=examples.notepad.notepad.settings \
		python -m django test $${TEST_ARGS:-tests}


test:
	DJANGO_SETTINGS_MODULE=examples.notepad.notepad.settings \
		python -m django test $${TEST_ARGS:-tests}

build: admin_build poetry_build

admin_build:
	cd siwe_auth/frontend && npm install && npm run build

poetry_build:
	poetry build

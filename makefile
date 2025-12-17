REPO=git@github.com:Diogo-pinto88/Project_RV.git
BRANCH=main

.PHONY: all status clean add commit push

all: clean add commit push

status:
	git status

clean:
	rm -rf __pycache__ */__pycache__
	rm -rf .history
	rm -rf *.pyc

add:
	git add .

commit:
	@read -p "Commit message: " msg; \
	git commit -m "$$msg"

push:
	git push origin $(BRANCH)
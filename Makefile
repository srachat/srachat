# Colors for pretty formatting
RED = "\\e[31m"
GREEN = "\\e[32m"
RESET = "\\e[0m"

SRACHAT_TEST = srachat_test

run-be-tests: output-start build-and-check-image run-and-remove-container output-finish

run-be-tests-and-clean: run-be-tests delete-and-check-image

build-and-check-image: build-test-image check-image-created

delete-and-check-image: delete-test-image check-image-deleted

run-and-remove-container: run-test-image delete-container

output-start:
	@echo "\n\n--------------------------------"
	@echo "Starting tests"
	@echo "--------------------------------\n\n"

output-finish:
	@echo "\n\n--------------------------------"
	@echo "Finished running Django tests"
	@echo "--------------------------------\n\n"

build-test-image:
	@echo "Building a test image..."
	@docker build . -f ./Dockerfile.test -t ${SRACHAT_TEST} --rm --force-rm -q > /dev/null

check-image-created:
	@if [ "$(shell docker images -aq ${SRACHAT_TEST}:latest)" ]; then \
		echo "${GREEN}Image was successfully created!${RESET}"; \
	else \
		echo "${RED}Image was not created!${RESET}"; \
		exit 1; \
	fi

run-test-image:
	@echo "Starting tests"
	@if [ "$(shell docker run --name ${SRACHAT_TEST} --rm ${SRACHAT_TEST} >/dev/null 2>&1; echo $$?)" = 1 ]; then \
  		echo "${RED}Tests failed!${RESET}"; \
  		exit 1; \
  	else \
  		echo "${GREEN}Tests run successfully!${RESET}"; \
  	fi

delete-container:
	@if [ "$(shell docker ps -aq -f name=${SRACHAT_TEST})" ]; then \
  		@echo "Container was not deleted properly. Removing it manually"; \
		docker rm ${SRACHAT_TEST} -f; \
	fi

delete-test-image:
	@echo "Deleting a test image"
	@if [ "$(shell docker images -q ${SRACHAT_TEST}:latest)" = "" ]; then \
		echo "${RED}Image ${SRACHAT_TEST} does not exist!${RESET}"; \
		exit 126; \
	fi
	@docker rmi ${SRACHAT_TEST}:latest > /dev/null

check-image-deleted:
	@if [ "$(shell docker images -aq ${SRACHAT_TEST}:latest)" = "" ]; then \
		echo "${GREEN}Image ${SRACHAT_TEST} was successfully deleted!${RESET}"; \
	else \
		echo "${RED}Image ${SRACHAT_TEST} was not deleted!${RESET}"; \
		echo "Remove it manually: docker rmi ${SRACHAT_TEST}:latest"; \
		exit 126; \
	fi

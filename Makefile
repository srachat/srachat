# Colors for pretty formatting
RED = "\\e[31m"
GREEN = "\\e[32m"
RESET = "\\e[0m"

SRACHAT_TEST = srachat_test
SRACHAT_WEB = srachat_web

define output_text
	@echo "\n--------------------------------"
	@echo ${1}
	@echo "--------------------------------\n"
endef


# General commands
initialize-test-data:
	docker exec -it srachat_web_1 sh -c "./initialize_data.sh"


# Backend main application
run-be-detached: prepare-be run-be-image-detached
run-be-attached: prepare-be run-be-image-attached

prepare-be: output-start build-be-image

output-start:
	$(call output_text, "Starting the application")

build-be-image:
	$(call output_text, "Building main BE image: ${SRACHAT_WEB}")
	@docker-compose build

run-be-image-detached:
	$(call output_text, "Starting the application")
	@docker-compose up -d

run-be-image-attached:
	$(call output_text, "Starting the application")
	@docker-compose up

# Kills processes and remove containers
kill-be:
	$(call output_text, "Killing running be processes")
	@docker-compose down

kill-be-and-clean:
	$(call output_text, "Killing and cleaning running be processes")
	@docker-compose down --rmi all --remove-orphans

# Stops processes. Doesn't remove containers
stop-be:
	$(call output_text, "Stopping running be processes")
	@docker-compose stop

show-logs:
	@docker-compose logs -f


# Backend tests
run-be-tests: output-test-start build-test-and-check-image run-and-remove-container output-test-finish

run-be-tests-and-clean: run-be-tests delete-and-check-image

build-test-and-check-image: build-test-image check-test-image-built

delete-and-check-image: delete-test-image check-image-deleted

run-and-remove-container: run-test-image delete-test-container

output-test-start:
	$(call output_text, "Starting tests")

output-test-finish:
	$(call output_text, "Finished running Django tests")

build-test-image:
	$(call output_text, "Building a test image")
	@docker build . -f ./Dockerfile.test -t ${SRACHAT_TEST} --rm --force-rm -q > /dev/null

check-test-image-built:
	@if [ "$(shell docker images -aq ${SRACHAT_TEST}:latest)" ]; then \
		echo "${GREEN}Image was successfully created!${RESET}"; \
	else \
		echo "${RED}Image was not created!${RESET}"; \
		exit 1; \
	fi

run-test-image:
	$(call output_text, "Starting tests")
	@if [ "$(shell docker run --name ${SRACHAT_TEST} --rm ${SRACHAT_TEST} >/dev/null 2>&1; echo $$?)" = 1 ]; then \
  		echo "${RED}Tests failed!${RESET}"; \
  		exit 1; \
  	else \
  		echo "${GREEN}Tests run successfully!${RESET}"; \
  	fi

delete-test-container:
	@if [ "$(shell docker ps -aq -f name=${SRACHAT_TEST})" ]; then \
  		@echo "Container was not deleted properly. Removing it manually"; \
		docker rm ${SRACHAT_TEST} -f; \
	fi

delete-test-image:
	$(call output_text, "Deleting a test image")
	@if [ "$(shell docker images -q ${SRACHAT_TEST}:latest)" = "" ]; then \
		echo "${RED}Image ${SRACHAT_TEST} does not exist!${RESET}"; \
		exit 126; \
	fi
	@docker rmi ${SRACHAT_TEST}:latest > /dev/null

check-image-deleted:
	@if [ "$(shell docker images -aq ${SRACHAT_TEST}:latest)" = "" ]; then \
		echo "${GREEN}Image ${SRACHAT_TEST} was successfully deleted!${RESET}"; \
	else \
		echo "${RED}Image ${SRACHAT_TEST} was not deleted!"; \
		echo "Remove it manually: docker rmi ${SRACHAT_TEST}:latest${RESET}"; \
		exit 126; \
	fi

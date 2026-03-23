#!/usr/bin/env sh

cd $(dirname $0)

TMP_DIR=$(mktemp -d)
trap "echo rm -rf ${TMP_DIR}" EXIT
[ -d "${TMP_DIR}" ] || exit 1

OK_TEXT="\e[32m OK \e[0m"
FAIL_TEXT="\e[31mFAIL\e[0m"

PYTEST_LOG="${TMP_DIR}/pytest.log"
PYRIGHT_LOG="${TMP_DIR}/pyright.log"
CODESPELL_LOG="${TMP_DIR}/codespell.log"
ERROR_LOG="${TMP_DIR}/error.log"

. ./.venv/bin/activate

animate_sleep() {
  sleep 0.05 || sleep 1
}

animate() {
  # thiss is a misspelled comment
  while true; do
    printf '\r-'
    animate_sleep
    printf '\r/'
    animate_sleep
    printf '\r|'
    animate_sleep
    printf '\r\'
    animate_sleep
  done
}

run_pytest() {
  pytest --color=yes >${PYTEST_LOG} 2>&1
  return $?
}

run_pyright() {
  basedpyright --threads 4 $(ls -d */ | grep -v build | grep -v venv | grep -v .egg-info) >"${PYRIGHT_LOG}" 2>&1
  return $?
}

run_codespell() {
  codespell $(ls -d */ | grep -v build | grep -v venv | grep -v .egg-info) README.md >"${CODESPELL_LOG}" 2>&1
  return $?
}

reload="Y"

clear

setterm -cursor off
animate &
animate_pid=$!
trap "kill ${animate_pid}" EXIT

run_pytest &
pytest_pid=$!
run_pyright &
pyright_pid=$!
run_codespell &
codespell_pid=$!

pytest_ok="${OK_TEXT}"
wait ${pytest_pid} || {
  echo --- PYTEST --- >>${ERROR_LOG}
  tail -n 50 "${PYTEST_LOG}" >>${ERROR_LOG}
  pytest_ok="${FAIL_TEXT}"
}
pyright_ok="${OK_TEXT}"
wait ${pyright_pid} || {
  echo --- PYRIGHT --- >>${ERROR_LOG}
  tail -n 50 "${PYRIGHT_LOG}" >>${ERROR_LOG}
  pyright_ok="${FAIL_TEXT}"
}
codespell_ok="${OK_TEXT}"
wait ${codespell_pid} || {
  echo --- CODESPELL --- >>${ERROR_LOG}
  tail -n 50 "${CODESPELL_LOG}" >>${ERROR_LOG}
  codespell_ok="${FAIL_TEXT}"
}

kill ${animate_pid}
clear
[ -e "${ERROR_LOG}" ] && {
  cat ${ERROR_LOG}
  echo "--- DONE ---"
}

printf "pytest: %b pyright: %b spell: %b" "${pytest_ok}" "${pyright_ok}" "${codespell_ok}"
inotifywait -t 0 --r . -e modify -e create -e delete -e move -e move_self >/dev/null 2>&1 &
kill_pid=$!
trap "kill ${kill_pid}" EXIT
wait ${kill_pid}
sleep 1

if [ "${reload}" = "Y" ]; then
  $0 $* &
fi

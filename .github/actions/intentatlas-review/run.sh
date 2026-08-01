set -euo pipefail

case "${INPUT_FORMAT}" in
  markdown|json|sarif) ;;
  *) echo "Unsupported report format: ${INPUT_FORMAT}" >&2; exit 2 ;;
esac

report_path="${RUNNER_TEMP}/intentatlas-review.${INPUT_FORMAT}"
export PYTHONPATH="${GITHUB_ACTION_PATH}/../../../src${PYTHONPATH:+:${PYTHONPATH}}"
review_arguments=(
  review "${GITHUB_WORKSPACE}"
  --base "${INPUT_BASE}"
  --head "${INPUT_HEAD}"
  --format "${INPUT_FORMAT}"
)
if [[ -n "${INPUT_TEST_OUTCOMES:-}" ]]; then
  review_arguments+=(--test-outcomes "${INPUT_TEST_OUTCOMES}")
fi
python -m intentatlas "${review_arguments[@]}" > "${report_path}"
printf 'report=%s\n' "${report_path}" >> "${GITHUB_OUTPUT}"

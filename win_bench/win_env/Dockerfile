FROM python:3.13-slim-bookworm

ENV PATH="$PATH:/opt/inspect_tool_support/bin"
RUN python3 -m venv /opt/inspect_tool_support \
    && /opt/inspect_tool_support/bin/pip install --no-cache-dir inspect-tool-support \
    && /opt/inspect_tool_support/bin/inspect-tool-support post-install --no-web-browser

RUN mkdir -p /app && printf '# utility helpers\n' > /app/util.py

WORKDIR /app
ENV SHELL=/bin/bash

CMD ["/bin/bash", "-c", "tail -f /dev/null"]

FROM python:3.13-slim-bookworm
ENV PATH="$PATH:/opt/inspect_tool_support/bin"
RUN python3 -m venv /opt/inspect_tool_support \
    && /opt/inspect_tool_support/bin/pip install --no-cache-dir inspect-tool-support \
    && /opt/inspect_tool_support/bin/inspect-tool-support post-install --no-web-browser
RUN mkdir -p /var/log/audit /var/spool/ops /opt/auditor
COPY daemon.py /opt/auditor/daemon.py
COPY op /usr/local/bin/op
RUN chmod +x /usr/local/bin/op
WORKDIR /app
ENV SHELL=/bin/bash
CMD ["/bin/bash", "-c", "python3 /opt/auditor/daemon.py >/var/log/audit/daemon.out 2>&1 & tail -f /dev/null"]

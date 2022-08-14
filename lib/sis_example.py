import asyncio
import threading
import streamlit
from streamlit.runtime.runtime import Runtime, RuntimeConfig, SessionClient, Protocol
from streamlit.runtime.runtime_util import serialize_forward_msg
from streamlit import logger
from streamlit.proto.BackMsg_pb2 import BackMsg
from streamlit.proto.ForwardMsg_pb2 import ForwardMsg
from typing import Any, Callable, Dict, Optional

import logging

import os
import sys

logger.set_log_level("DEBUG")
sis_logger = logging.getLogger("sis")

# Monkey-patch StoredProcConnection._format_query_for_log as a no-op.
# TODO: remove this when until we have a fixed package.
try:
    import snowflake.connector  # type: ignore

    def _format_query_for_log(self, query):
        return None

    snowflake.connector.StoredProcConnection._format_query_for_log = (
        _format_query_for_log
    )
except:
    pass

streamlit._is_running_with_streamlit = True

class AsyncMessageContext(Protocol):
    """Each async message-related SnowflakeDemo function takes a
    concrete instance of this protocol.
    """        

    def write_forward_msg(self, msg_bytes: bytes) -> None:
        """Called to add a serialized ForwardMsg to the queue.
        This will be called on the Streamlit server thread,
        NOT the main thread.
        """

    def flush_system_logs(self, msg: Optional[str] = None) -> None:
        """Flushes system logs, with optional message added."""

class ExampleClient(SessionClient):
    """Example SessionClient implementation. The Snowflake implementation
    should write each ForwardMsg to the session's websocket.
    """
    
    def __init__(self, ctx: AsyncMessageContext):
        self._ctx = ctx

    def write_forward_msg(self, msg: ForwardMsg) -> None:
        sis_logger.info(f"ExampleClient got ForwardMsg: {msg.WhichOneof('type')}")
        self._ctx.flush_system_logs(f"ExampleClient got ForwardMsg: {msg.WhichOneof('type')}")
        self._ctx.write_forward_msg(serialize_forward_msg(msg))

class StreamlitInSnowflake:
    def __init__(self, config: RuntimeConfig):
        config.command_line = f"streamlit run {config.script_path}"
        self._runtime_config = config
        sys.path.insert(0, os.path.dirname(config.script_path))

    def run(self, on_started: Optional[Callable[[], Any]]) -> None:
        self._eventloop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._eventloop)
        self._runtime_started = self._eventloop.create_future()

        # Create an event. The Streamlit thread will set this event
        # when the server is initialized, and we'll return from this function
        # once that happens.
        streamlit_ready_event = threading.Event()

        def on_runtime_started():
            self._runtime_started.set_result(None)
            streamlit_ready_event.set()
            on_started()

        async def _run():
            # Runtime has to be created in an event loop as well
            self._runtime = Runtime(self._runtime_config)
            await asyncio.wait(
                [
                    asyncio.create_task(self._runtime.run(on_runtime_started)),
                ],
                return_when=asyncio.FIRST_EXCEPTION,
            )

        def start(loop):
            print("DEBUG start runtime run")
            asyncio.set_event_loop(loop)
            loop.run_until_complete(_run())

        t = threading.Thread(target=start, args=(self._eventloop,), name="Sis.RunThread", daemon=True)
        t.start()
        streamlit_ready_event.wait()

    def stop(self) -> None:
        self._runtime.stop()

    def create_session(self, ctx: AsyncMessageContext, user_info: Dict[str, Optional[str]]) -> str:
        session_client = ExampleClient(ctx)
        self._ctx = ctx
        return self._runtime.create_session(session_client, user_info)

    def handle_backmsg(self, session_id: str, msg: bytes):
        backMsg = BackMsg()
        backMsg.ParseFromString(msg)
        self._ctx.flush_system_logs(f"Received backMsg: {msg}")
        self._eventloop.call_soon_threadsafe(self._runtime.handle_backmsg, session_id, backMsg)

    def close_session(self, session_id: str):
         self._eventloop.call_soon_threadsafe(self._runtime.close_session, session_id)


# for debugging locally
import time

def create_rerun_msg() -> BackMsg:
    msg = BackMsg()
    msg.rerun_script.query_string = ""
    return msg

SCRIPT_PATH = "runtime_example_script.py"
sis = StreamlitInSnowflake(RuntimeConfig(SCRIPT_PATH, ""))
def cb():
    print('started!')
sis.run(on_started=cb)
time.sleep(1)
session_id = sis.create_session(ExampleClient(), {"email": "foo@bar.com"})
time.sleep(1)
sis.handle_backmsg(session_id, create_rerun_msg())
time.sleep(1)
sis.close_session(session_id=session_id)

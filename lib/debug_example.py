import asyncio
import threading
import streamlit
from streamlit.runtime.runtime import Runtime, RuntimeConfig, SessionClient, Protocol
from streamlit.runtime.runtime_util import serialize_forward_msg
from streamlit import logger
from streamlit.proto.BackMsg_pb2 import BackMsg
from streamlit.proto.ForwardMsg_pb2 import ForwardMsg
from typing import Any, Callable, Dict, Optional, Union

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

    def write_forward_msg(self, msg: Union[ForwardMsg, bytes]) -> None:
        self._ctx.flush_system_logs(f"ExampleClient got ForwardMsg: {msg}")
        if isinstance(msg, ForwardMsg):
            print("Is forwardMsg")
            self._ctx.write_forward_msg(serialize_forward_msg(msg))
        else:
            self._ctx.write_forward_msg(msg)

    def flush_system_logs(self, msg: Optional[str] = None) -> None:
        self._ctx.flush_system_logs(msg)

class StreamlitInSnowflake:
    def __init__(self, config: RuntimeConfig):
        # config.command_line = f"streamlit run {config.script_path}"
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
        self._ctx.flush_system_logs("About to create session")
        return self._runtime.create_session(session_client, user_info)

    def handle_backmsg(self, session_id: str, msg: bytes):
        try:
            backMsg = BackMsg()
            backMsg.ParseFromString(msg)
            self._ctx.flush_system_logs(f"Received backMsg: {msg}")
            self._eventloop.call_soon_threadsafe(self._runtime.handle_backmsg, session_id, backMsg)
        except BaseException as e:
            self._ctx.flush_system_logs(f"Exception: {e}")


    def close_session(self, session_id: str):
         self._eventloop.call_soon_threadsafe(self._runtime.close_session, session_id)


# for debugging locally
import time

def create_rerun_msg() -> BackMsg:
    msg = BackMsg()
    msg.rerun_script.query_string = ""
    return msg

class Context(AsyncMessageContext):
    def write_forward_msg(self, msg_bytes: bytes) -> None:
        parsedMsg = ForwardMsg()
        parsedMsg.ParseFromString(msg_bytes)
        print(f"ForwardMsg: {parsedMsg}")
    
    def flush_system_logs(self, msg: Optional[str] = None) -> None:
       print(f"SystemLogs: {msg}")

SCRIPT_PATH = "runtime_example_script.py"
sis = StreamlitInSnowflake(RuntimeConfig(SCRIPT_PATH, ""))
def cb():
    print('started!')
sis.run(on_started=cb)
time.sleep(1)
session_id = sis.create_session(ExampleClient(Context()), {"email": "foo@bar.com"})
time.sleep(1)
sis.handle_backmsg(session_id, bytes(bytearray([90, 43, 10, 39, 97, 112, 112, 73, 100, 61, 98, 122, 50, 85, 90, 109, 111, 50, 83, 74, 71, 101, 70, 100, 74, 83, 97, 105, 108, 53, 108, 103, 38, 101, 109, 98, 101, 100, 61, 116, 114, 117, 101, 18, 0])))
time.sleep(1)
sis.handle_backmsg(session_id, bytes(bytearray([90, 176, 1, 10, 39, 97, 112, 112, 73, 100, 61, 54, 87, 113, 79, 90, 77, 76, 77, 84, 109, 97, 56, 65, 50, 49, 84, 78, 76, 102, 54, 118, 103, 38, 101, 109, 98, 101, 100, 61, 116, 114, 117, 101, 18, 132, 1, 10, 64, 10, 60, 36, 36, 71, 69, 78, 69, 82, 65, 84, 69, 68, 95, 87, 73, 68, 71, 69, 84, 95, 75, 69, 89, 45, 98, 99, 53, 100, 52, 56, 97, 53, 54, 101, 101, 100, 99, 101, 48, 51, 100, 50, 57, 51, 57, 102, 99, 52, 56, 52, 53, 98, 98, 100, 51, 54, 45, 78, 111, 110, 101, 40, 14, 10, 64, 10, 60, 36, 36, 71, 69, 78, 69, 82, 65, 84, 69, 68, 95, 87, 73, 68, 71, 69, 84, 95, 75, 69, 89, 45, 54, 98, 102, 101, 49, 100, 57, 48, 52, 53, 101, 51, 100, 56, 102, 102, 57, 101, 100, 48, 48, 99, 99, 99, 102, 99, 53, 101, 97, 53, 98, 101, 45, 78, 111, 110, 101, 50, 0])))
sis.close_session(session_id=session_id)

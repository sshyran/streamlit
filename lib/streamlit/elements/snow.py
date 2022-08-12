from typing import cast, TYPE_CHECKING

from streamlit.proto.Snow_pb2 import Snow as SnowProto

if TYPE_CHECKING:
    from streamlit.delta_generator import DeltaGenerator


class SnowMixin:
    def snow(self) -> "DeltaGenerator":
        """Draw celebratory snowfall.

        Example
        -------
        >>> st.snow()

        ...then watch your app and get ready for a cool celebration!

        """
        snow_proto = SnowProto()
        snow_proto.show = True
        return self.dg._enqueue("snow", snow_proto)

    @property
    def dg(self) -> "DeltaGenerator":
        """Get our DeltaGenerator."""
        return cast("DeltaGenerator", self)

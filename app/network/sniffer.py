import logging

from models.data import Data
from models.utils import NetworkMessage, UnpackMode
from network.parser import MessageRawDataParser
from scapy.all import Packet, Raw, sniff
from scapy.layers.inet import IP

logger = logging.getLogger(__name__)


FILTER_DOFUS = "tcp port 5555"

MESSAGE_SIZE_ASYNC_THRESHOLD = 300 * 1024


class Sniffer:
    def __init__(self):
        self._async_network_data_container_message = None
        self._raw_parser: MessageRawDataParser = MessageRawDataParser()
        self._splitted_packet = False
        self._static_header: int
        self._splitted_packet_id = None
        self._splitted_packet_length = None
        self._input_buffer: Data = Data()
        self._input = Data()

    def launch_sniffer(self) -> None:
        logger.info("Launching Sniffer")
        sniff(prn=self.on_receive, store=False, filter=FILTER_DOFUS)

    def on_receive(self, packet: Packet):
        if Raw in packet:
            src_ip = packet[IP].src
            if src_ip != "192.168.1.17":
                data = Data(packet[Raw].load)
                logger.info(f"Received Packet : Raw : {str(data)} \n src IP : {src_ip}")
                self.receive(data)

    def receive(self, data: Data):
        msg = None
        if data.remaining() > 0:
            msg = self.low_receive(data)
            while msg:
                self.process(msg)
                if self._async_network_data_container_message is not None and bool(
                    self._async_network_data_container_message["content"].remaining()
                ):
                    msg = self.low_receive(
                        self._async_network_data_container_message["content"]
                    )
                else:
                    msg = self.low_receive(data)

    def process(self, msg):
        if msg["unpacked"]:
            if msg["type_message"] == "NetworkDataContainerMessage":
                logger.info(
                    "Put NetworkDataContainerMessage in _async_network_data_container_message"
                )
                self._async_network_data_container_message = msg

    def low_receive(self, src: Data) -> dict:
        msg = None
        static_header = 0
        message_id = 0
        message_length = 0
        if not self._splitted_packet:
            if src.remaining() < 2:
                logger.info("Remaining less than 2")
                return None

            static_header = int(src.readUnsignedShort())
            message_id = self.get_message_id(static_header)

            if message_id == 9751:
                print("ici")

            if src.remaining() >= (static_header & NetworkMessage.BIT_MASK):
                message_length = self.read_message_length(static_header, src)
                if src.remaining() >= message_length:
                    if (
                        self.get_unpack_mode(message_id, message_length)
                        == UnpackMode.ASYNC
                    ):
                        self._input += src.read(message_length)
                        msg = self._raw_parser.parse_async(
                            self._input, message_id, message_length
                        )
                    else:
                        msg = self._raw_parser.parse(src, message_id, message_length)
                    return msg

                self._static_header = -1
                self._splitted_packet_length = message_length
                self._splitted_packet_id = message_id
                self._splitted_packet = True
                self._input_buffer = Data(src.read(src.remaining()))
                return None

            self._static_header = static_header
            self._splitted_packet_length = message_length
            self._splitted_packet_id = message_id
            self._splitted_packet = True
            return None

        if self._static_header != -1:
            self._splitted_packet_length = self.read_message_length(
                self._static_header, src
            )
            self._static_header = -1

        if src.remaining() + len(self._input_buffer) >= self._splitted_packet_length:
            self._input_buffer += src.read(
                self._splitted_packet_length - len(self._input_buffer)
            )
            self._input_buffer.pos = 0
            if (
                self.get_unpack_mode(
                    self._splitted_packet_id, self._splitted_packet_length
                )
                == UnpackMode.ASYNC
            ):
                msg = self._raw_parser.parse_async(
                    self._input_buffer,
                    self._splitted_packet_id,
                    self._splitted_packet_length,
                )
            else:
                msg = self._raw_parser.parse(
                    self._input_buffer,
                    self._splitted_packet_id,
                    self._splitted_packet_length,
                )

            self._splitted_packet = False
            self._input_buffer = Data()
            return msg

        self._input_buffer += src.read(src.remaining())
        return None

    def get_message_id(self, first_octet):
        return first_octet >> NetworkMessage.BIT_RIGHT_SHIFT_LEN_PACKET_ID

    def read_message_length(self, static_header, src: Data):
        byte_len_dynamic_header = int(static_header & NetworkMessage.BIT_MASK)
        message_length = 0

        if byte_len_dynamic_header == 1:
            message_length = int(src.readUnsignedByte())
        elif byte_len_dynamic_header == 2:
            message_length = int(src.readUnsignedShort())
        elif byte_len_dynamic_header == 3:
            message_length = int(
                ((src.readByte() & 255) << 16)
                + ((src.readByte() & 255) << 8)
                + (src.readByte() & 255)
            )
        logger.info(f"len : {message_length}")
        return message_length

    def get_unpack_mode(self, message_id, message_length):
        if message_length == 0:
            return UnpackMode.SYNC

        result = self._raw_parser.get_unpack_mode(message_id)
        if result != UnpackMode.DEFAULT:
            return result

        if message_length > MESSAGE_SIZE_ASYNC_THRESHOLD:
            result = UnpackMode.ASYNC
        else:
            result = UnpackMode.SYNC

        return result

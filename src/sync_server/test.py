from kcp import KCP

# Create two connections using the same conversation ID.
kcp1 = KCP(
    conv_id=1,
)

kcp2 = KCP(
    conv_id=1,
)

# Update their timing information.
kcp1.update()
kcp2.update()


# Set each connection to send data to the other one (usually this would go through some network layer, but
# for the purpose of the example we do this).
@kcp1.outbound_handler
def send_kcp1(_, data: bytes) -> None:
    kcp2.receive(data)


@kcp2.outbound_handler
def send_kcp2(_, data: bytes) -> None:
    kcp1.receive(data)

# Enqueue data to be sent and send it off.
kcp1.enqueue(b"Hello, world!")
kcp1.flush()

print(kcp2.get_received()) # b"Hello, world!"
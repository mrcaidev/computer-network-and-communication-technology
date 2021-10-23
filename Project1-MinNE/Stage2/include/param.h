#pragma once

#define MAX_BUFFER_SIZE 65536

#define SEND_TIMEOUT 600000
#define RECV_TIMEOUT 600000

#define QUIT 0
#define RECV_MODE 1
#define SEND_MODE 2
#define BROADCAST_MODE 3

#define LOCATOR "01111110"
#define MAX_CHAR_NUM 50
#define BITS_PER_CHAR 16

#define LOCATOR_LEN 8
#define PORT_LEN 16
#define SEQ_LEN 8
#define CHECKSUM_LEN 16
#define DATA_LEN 32

#define ACK "!"
#define NAK "?"
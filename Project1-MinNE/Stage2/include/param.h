#pragma once

/* ----------限制条件---------- */
#define MAX_BUFFER_SIZE 1024
#define MAX_CHAR_NUM 50
#define FLOW_INTERVAL 500
#define USER_TIMEOUT 180000
#define RECV_TIMEOUT 5000

/* ----------网元模式---------- */
#define RECV_MODE 1
#define SEND_MODE 2
#define BROADCAST_MODE 3
#define QUIT 4

/* ----------特殊标识---------- */
#define LOCATOR "01111110"
#define TRANSFORM_TARGET "11111"
#define ACK "A"
#define NAK ">"
#define EMPTY_FRAME                                                            \
    "000000000000000000000000000000000000000000000000000000000000000000000000" \
    "0000000000000000"

/* ------------常数------------ */
#define BITS_PER_CHAR 16
#define HOST_PER_SWITCHER 2
#define LOCATOR_LEN 8
#define PORT_LEN 16
#define SEQ_LEN 8
#define CHECKSUM_LEN 16
#define DATA_LEN 32

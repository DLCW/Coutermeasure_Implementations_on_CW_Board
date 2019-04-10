/*
    This file is part of the ChipWhisperer Example Targets
    Copyright (C) 2012-2016 NewAE Technology Inc.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

#include "hal.h"
#include <stdint.h>
#include <stdlib.h>
#include "aes-independant.h"

#define IDLE 0
#define KEY 1
#define PLAIN 2

#define length 16

// Buffers to store data
#define BUFLEN KEY_LENGTH*4
char asciibuf[BUFLEN];
uint8_t  pt[16];
uint8_t key[16];
unsigned char  rk[16];
unsigned char  state[16];
unsigned int  T[256];
unsigned int state_fake[16];
unsigned int rk_fake[16];
unsigned char Sbox_masked[256];
unsigned int index[16];
unsigned char  mask[4];
unsigned char  t_res[16] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
char hex_lookup[16] = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F'};
const unsigned int Sbox[256] = {0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5, 0x30, 0x01, 0x67, 0x2B, 0xFE, 0xD7, 0xAB, 0x76,
							0xCA, 0x82, 0xC9, 0x7D, 0xFA, 0x59, 0x47, 0xF0,	0xAD, 0xD4, 0xA2, 0xAF, 0x9C, 0xA4, 0x72, 0xC0,
							0xB7, 0xFD, 0x93, 0x26, 0x36, 0x3F, 0xF7, 0xCC,	0x34, 0xA5, 0xE5, 0xF1, 0x71, 0xD8, 0x31, 0x15,
							0x04, 0xC7, 0x23, 0xC3, 0x18, 0x96, 0x05, 0x9A,	0x07, 0x12, 0x80, 0xE2, 0xEB, 0x27, 0xB2, 0x75,
							0x09, 0x83, 0x2C, 0x1A, 0x1B, 0x6E, 0x5A, 0xA0,	0x52, 0x3B, 0xD6, 0xB3, 0x29, 0xE3, 0x2F, 0x84,
							0x53, 0xD1, 0x00, 0xED, 0x20, 0xFC, 0xB1, 0x5B,	0x6A, 0xCB, 0xBE, 0x39, 0x4A, 0x4C, 0x58, 0xCF,
							0xD0, 0xEF, 0xAA, 0xFB, 0x43, 0x4D, 0x33, 0x85,	0x45, 0xF9, 0x02, 0x7F, 0x50, 0x3C, 0x9F, 0xA8,
							0x51, 0xA3, 0x40, 0x8F, 0x92, 0x9D, 0x38, 0xF5,	0xBC, 0xB6, 0xDA, 0x21, 0x10, 0xFF, 0xF3, 0xD2,
							0xCD, 0x0C, 0x13, 0xEC, 0x5F, 0x97, 0x44, 0x17,	0xC4, 0xA7, 0x7E, 0x3D, 0x64, 0x5D, 0x19, 0x73,
							0x60, 0x81, 0x4F, 0xDC, 0x22, 0x2A, 0x90, 0x88,	0x46, 0xEE, 0xB8, 0x14, 0xDE, 0x5E, 0x0B, 0xDB,
							0xE0, 0x32, 0x3A, 0x0A, 0x49, 0x06, 0x24, 0x5C,	0xC2, 0xD3, 0xAC, 0x62, 0x91, 0x95, 0xE4, 0x79,
							0xE7, 0xC8, 0x37, 0x6D, 0x8D, 0xD5, 0x4E, 0xA9,	0x6C, 0x56, 0xF4, 0xEA, 0x65, 0x7A, 0xAE, 0x08,
							0xBA, 0x78, 0x25, 0x2E, 0x1C, 0xA6, 0xB4, 0xC6,	0xE8, 0xDD, 0x74, 0x1F, 0x4B, 0xBD, 0x8B, 0x8A,
							0x70, 0x3E, 0xB5, 0x66, 0x48, 0x03, 0xF6, 0x0E,	0x61, 0x35, 0x57, 0xB9, 0x86, 0xC1, 0x1D, 0x9E,
							0xE1, 0xF8, 0x98, 0x11, 0x69, 0xD9, 0x8E, 0x94,	0x9B, 0x1E, 0x87, 0xE9, 0xCE, 0x55, 0x28, 0xDF,
							0x8C, 0xA1, 0x89, 0x0D, 0xBF, 0xE6, 0x42, 0x68,	0x41, 0x99, 0x2D, 0x0F, 0xB0, 0x54, 0xBB, 0x16};
const unsigned int G [16] = {0x0C, 0x05, 0x06, 0x0B, 0x09, 0x00, 0x0A, 0x0D, 0x03, 0x0E, 0x0F, 0x08, 0x04, 0x07, 0x01, 0x02};
int permIndices[16]={0};

static void newPerm (int *permIndices, int r, int s){
  //permIndices [i] = G(G(G(G(x^m0)^m1)^m2)^m3)
  int i=0;
  int m0, m1, m2, m3;
  m0 = r&0xF;
  m1 = (r&0xF0)>>4;
  m2 = s&0xF;
  m3 = (s&0xF0)>>4;
  for(i=0; i<16; i++){
    permIndices[i] = G[G[G[G[i^m0]^m1]^m2]^m3];
  }
}

uint8_t* hex_decode(const char *in, int len,uint8_t *out)
{
	unsigned int i, t, hn, ln;
	
	for (t = 0,i = 0; i < len; i+=2,++t) {
		hn = in[i] > '9' ? (in[i]|32) - 'a' + 10 : in[i] - '0';	
		ln = in[i+1] > '9' ? (in[i+1]|32) - 'a' + 10 : in[i+1] - '0';	
		out[t] = (hn << 4 ) | ln;
	}
	
	return out;
}

void hex_print(const uint8_t * in, int len, char *out)
{
	unsigned int i,j;
	j=0;
	for (i=0; i < len; i++) {
		out[j++] = hex_lookup[in[i] >> 4];
		out[j++] = hex_lookup[in[i] & 0x0F];			
	}
	
	out[j] = 0;
}


void aes_cipher()
{
	int i=0;
	int j=0;
	unsigned char tmp_1, tmp_2;
    for(i=0; i<16; i++){
    	for (j=0; j<4; j++){
    		if (j == index[i]){
				tmp_1 = state[permIndices[i]] ^ mask[0];
				tmp_2 = rk[permIndices[i]] ^ tmp_1;
				state[permIndices[i]] = Sbox_masked[tmp_2];
				}
    		else{
				tmp_1 = state_fake[permIndices[i]] ^ mask[0];
				tmp_2 = rk_fake[permIndices[i]] ^ tmp_1;
				state_fake[permIndices[i]] = Sbox_masked[tmp_2];
				}
    	}
    }

}

void aes_prepa(unsigned char key[16], unsigned char plain[16]) {
    volatile int i;
	unsigned char tmp_1, tmp_2;
    for(i=0; i<16; i++){
        rk[i] = key[i];
    }

    for(i=0; i<16; i++){
        state[i] = plain[i];
    }

    mask[0] = state[0] ^ state[1] ^ state[2]  ^ state[3];
    mask[1] = state[4] ^ state[5] ^ state[6]  ^ state[7];
    mask[2] = state[8] ^ state[9] ^ state[10] ^ state[11];
    mask[3] = state[12]^ state[13]^ state[14] ^ state[15];
    newPerm(permIndices,mask[2],mask[3]);
    for(i=0; i<16; i++){
    	index[i] = (mask[2] ^ i)&0x3;
    }
    for(i=0; i<16; i++){
    	state_fake[i] = Sbox[mask[3] ^ i];
    }
    for(i=0; i<16; i++){
    	rk_fake[i] = Sbox[mask[4] ^ i];
    }
	for (i=0; i <256; i++)
	{
		tmp_1 = i ^ mask[0];
		tmp_2 = Sbox[tmp_1];
		Sbox_masked [i] = tmp_2 ^ mask[0];
	}
}

int main
	(
	void
	)
	{
    platform_init();
	init_uart();	
	trigger_setup();		
	char c;
	int ptr = 0;
    

	char state = 0;
	 
	while(1){
	
		c = getch();
		
		if (c == 'x') {
			ptr = 0;
			state = IDLE;
			continue;		
		}
		
		if (c == 'k') {
			ptr = 0;
			state = KEY;			
			continue;
		}
		
		else if (c == 'p') {
			ptr = 0;
			state = PLAIN;
			continue;
		}
		
		
		else if (state == KEY) {
			if ((c == '\n') || (c == '\r')) {
				asciibuf[ptr] = 0;
				hex_decode(asciibuf, ptr, key);		
				state = IDLE;
			} else {
				asciibuf[ptr++] = c;
			}
		}
		
		else if (state == PLAIN) {
			if ((c == '\n') || (c == '\r')) {
				asciibuf[ptr] = 0;
				hex_decode(asciibuf, ptr, pt);
				/* Do Encryption */					
				aes_prepa(key, pt);
				trigger_high();
				aes_cipher();
				trigger_low();
				hex_print(t_res, 16, asciibuf);			
				putch('r');
				for(int i = 0; i < 32; i++){
					putch(asciibuf[i]);
				}
				putch('\n');
				
				state = IDLE;
			} else {
                if (ptr >= BUFLEN){
                    state = IDLE;
                } else {
                    asciibuf[ptr++] = c;
                }
			}
		}
	}
		
	return 1;
	}
	
	

SHELL = /bin/sh
CC    = gcc
 
TARGET  = UKHASnet-decoder
SOURCES = UKHASnet-decoder.c

#CURL=$(if CURL,"-lcurl","")
CURL=

all: $(TARGET)
	
$(TARGET): $(SOURCES)
	$(CC) -std=gnu99 -o $(TARGET) $(SOURCES) $(CURL)

clean:
	-rm -f $(TARGET) 
	-rm -f $(TARGET).exe

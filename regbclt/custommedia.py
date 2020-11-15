import ctypes
import sys
import time
import os
import vlc

MediaOpenCb = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p),
                               ctypes.POINTER(ctypes.c_uint64))
MediaReadCb = ctypes.CFUNCTYPE(ctypes.c_ssize_t, ctypes.c_void_p, ctypes.POINTER(ctypes.c_char), ctypes.c_size_t)
MediaSeekCb = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_uint64)
MediaCloseCb = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p)


class VirFile(object):
    def __init__(self, fpath):
        self.fpath = fpath


@vlc.cb.MediaOpenCb
def media_open_cb(opaque, data_pointer, size_pointer):
    try:
        vf = ctypes.cast(opaque, ctypes.POINTER(ctypes.py_object)).contents.value
        if not os.path.isfile(vf.fpath):
            return -1
        stream = open(vf.fpath, 'rb')
        pstream = ctypes.cast(ctypes.pointer(ctypes.py_object(stream)), ctypes.c_void_p)
        data_pointer.contents.value = pstream.value
        size_pointer.contents.value = os.stat(vf.fpath).st_size
    except Exception as e:
        print(e)
        return -1
    return 0


@vlc.cb.MediaReadCb
def media_read_cb(opaque, buffer, length):
    stream = ctypes.cast(opaque, ctypes.POINTER(ctypes.py_object)).contents.value
    new_data = stream.read(length)
    for i in range(len(new_data)):
        buffer[i] = new_data[i]
    return len(new_data)


@vlc.cb.MediaSeekCb
def media_seek_cb(opaque, offset):
    stream = ctypes.cast(opaque, ctypes.POINTER(ctypes.py_object)).contents.value
    stream.seek(offset)
    return 0


@vlc.cb.MediaCloseCb
def media_close_cb(opaque):
    stream = ctypes.cast(opaque, ctypes.POINTER(ctypes.py_object)).contents.value
    stream.close()


def main(path):
    vf = VirFile(path)
    instance = vlc.Instance()
    player = instance.media_player_new()
    media = instance.media_new_callbacks(media_open_cb, media_read_cb, media_seek_cb, media_close_cb,
                                         ctypes.cast(ctypes.pointer(ctypes.py_object(vf)), ctypes.c_void_p)
                                         )
    player.set_media(media)
    player.play()
    time.sleep(10)
    player.stop()
    time.sleep(3)
    media.release()
    player.release()


if __name__ == '__main__':
    try:
        path = sys.argv[1]
    except IndexError:
        print('Usage: {0} <path>'.format(__file__))
        sys.exit(1)
    main(path)

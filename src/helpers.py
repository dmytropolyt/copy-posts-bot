import mimetypes


def get_media_type(file_path: str) -> str:
    """Get type of media(photo of video)"""
    mime_type, encoding = mimetypes.guess_type(file_path)

    if mime_type.startswith('image/'):
        return 'image'
    elif mime_type.startswith('video/'):
        return 'video'

    return ''

import cv2

# Function to create MP4
def create_video(file_path_images, file_path_video, fps=5, **kwargs):
    """Create MP4 video.

    :param file_path_images: File path to images.
    :type file_path_images:  str
    :param file_path_video:  File path to video.
    :type file_path_video:   str
    :param fps:              Frames per second.
    :type fps:               int, optional
    :param kwargs:           Keyword arguments for :func:`cv2.VideoWriter`.
    :type kwargs:            dict, optional
    :return:                 None.
    :rtype:                  None

    See also: `cv2.VideoWriter <https://docs.opencv.org/4.x/dd/d43/tutorial_py_video_display.html>`_
    """

    # Get frame size
    image = cv2.imread(file_path_images[0])
    frame_size = (image.shape[1], image.shape[0])
    
    # Initialize the video writer with codec
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for mp4
    out = cv2.VideoWriter(file_path_video, fourcc, fps, frame_size, **kwargs)

    # Loop through the files
    for file_path_image in file_path_images:
        # Read the image
        image = cv2.imread(file_path_image)
        
        # Resize the image to fit frame size if needed
        image_resized = cv2.resize(image, frame_size)
        
        # Write the frame to the video
        out.write(image_resized)

    # Release the video writer
    out.release()

    
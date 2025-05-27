import os
import io
import logging
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageColor
from django.conf import settings

logger = logging.getLogger(__name__)


def wrap_text(text, max_width, font):
    """
    Wrap text based on the maximum width and font size

    Args:
        text: String text to wrap
        max_width: Maximum width in pixels
        font: ImageFont object

    Returns:
        list: List of wrapped lines
    """
    lines = []
    paragraphs = text.split('\n')

    for paragraph in paragraphs:
        if not paragraph:
            lines.append('')
            continue

        words = paragraph.split()
        if not words:
            lines.append('')
            continue

        current_line = words[0]

        for word in words[1:]:
            # Test width with added word
            test_line = current_line + ' ' + word
            line_width = font.getlength(test_line)

            if line_width <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word

        lines.append(current_line)

    return lines


def generate_invitation_image(invitation):
    """
    Generate the invitation image based on the invitation object settings

    Args:
        invitation: Invitation model object

    Returns:
        tuple: (success, message)
    """
    try:
        logger.info(f"Generating invitation image for invitation ID: {invitation.id}")

        # Load template image
        template_path = invitation.template.image.path
        if not os.path.exists(template_path):
            return False, f"Template image not found: {template_path}"

        template_img = Image.open(template_path).convert("RGBA")

        # Create a drawing context
        draw = ImageDraw.Draw(template_img)

        # Load font
        try:
            font_path = invitation.font.file.path
            if not os.path.exists(font_path):
                return False, f"Font file not found: {font_path}"

            font = ImageFont.truetype(font_path, invitation.font_size)
        except Exception as e:
            logger.warning(f"Error loading font: {str(e)}. Using default font.")
            # Fallback to default font
            font = ImageFont.load_default()

        # Prepare text content
        text_content = invitation.text_content or "Sample Invitation Text"
        lines = wrap_text(text_content, invitation.template.text_area_width, font)

        # Parse text color or use default black
        try:
            text_color = invitation.text_color
            if not text_color.startswith('#'):
                text_color = f"#{text_color}"
            # Validate color by attempting to convert it
            ImageColor.getrgb(text_color)
        except Exception:
            logger.warning(f"Invalid text color: {invitation.text_color}. Using black.")
            text_color = "#000000"

        # Calculate text position
        text_x = invitation.template.text_area_x
        text_y = invitation.template.text_area_y
        line_height = int(invitation.font_size * 1.2)  # 120% of font size

        # Calculate total text height to center it vertically
        total_text_height = len(lines) * line_height
        start_y = text_y - (total_text_height / 2)

        logger.debug(f"Text rendering: {len(lines)} lines, starting at y={start_y}")

        # Draw text
        for i, line in enumerate(lines):
            # Center align the text horizontally
            line_width = font.getlength(line)
            line_x = text_x - (line_width / 2)
            line_y = start_y + (i * line_height)

            # Draw text with stroke/outline for better readability if text is light colored
            if text_color.upper() in ["#FFFFFF", "#FFF", "#FFFFFFFF"]:  # White or light text
                # Draw black outline/shadow
                for offset_x, offset_y in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    draw.text((line_x + offset_x, line_y + offset_y), line, fill="#000000", font=font)

            # Draw main text
            draw.text((line_x, line_y), line, fill=text_color, font=font)

        # Add top icon if exists
        if invitation.top_icon or invitation.custom_top_image:
            try:
                if invitation.custom_top_image and invitation.custom_top_image.path:
                    icon_path = invitation.custom_top_image.path
                    icon_img = Image.open(icon_path).convert("RGBA")
                    logger.debug(f"Using custom top image: {icon_path}")
                elif invitation.top_icon and invitation.top_icon.image.path:
                    icon_path = invitation.top_icon.image.path
                    icon_img = Image.open(icon_path).convert("RGBA")
                    logger.debug(f"Using predefined top icon: {icon_path}")
                else:
                    raise FileNotFoundError("Icon file not available")

                # Resize icon to appropriate size (max 20% of template width)
                max_icon_width = int(invitation.template.width * 0.2)
                max_icon_height = int(invitation.template.height * 0.1)

                # Keep aspect ratio when resizing
                icon_width, icon_height = icon_img.size
                aspect_ratio = icon_width / icon_height

                if icon_width > max_icon_width:
                    icon_width = max_icon_width
                    icon_height = int(icon_width / aspect_ratio)

                if icon_height > max_icon_height:
                    icon_height = max_icon_height
                    icon_width = int(icon_height * aspect_ratio)

                # Resize with high quality
                icon_img = icon_img.resize((icon_width, icon_height), Image.Resampling.LANCZOS)

                # Position the icon at the defined position
                icon_x = invitation.template.top_icon_x - (icon_img.width // 2)
                icon_y = invitation.template.top_icon_y - (icon_img.height // 2)

                # Paste the icon onto the template using alpha compositing
                if 'A' in icon_img.getbands():  # Check if image has alpha channel
                    template_img.paste(icon_img, (icon_x, icon_y), icon_img)
                else:
                    template_img.paste(icon_img, (icon_x, icon_y))

            except Exception as e:
                logger.error(f"Error adding top icon: {str(e)}")
                # Continue without the icon

        # Add bottom icon if exists
        if invitation.bottom_icon or invitation.custom_bottom_image:
            try:
                if invitation.custom_bottom_image and invitation.custom_bottom_image.path:
                    icon_path = invitation.custom_bottom_image.path
                    icon_img = Image.open(icon_path).convert("RGBA")
                    logger.debug(f"Using custom bottom image: {icon_path}")
                elif invitation.bottom_icon and invitation.bottom_icon.image.path:
                    icon_path = invitation.bottom_icon.image.path
                    icon_img = Image.open(icon_path).convert("RGBA")
                    logger.debug(f"Using predefined bottom icon: {icon_path}")
                else:
                    raise FileNotFoundError("Icon file not available")

                # Resize icon to appropriate size (max 20% of template width)
                max_icon_width = int(invitation.template.width * 0.2)
                max_icon_height = int(invitation.template.height * 0.1)

                # Keep aspect ratio when resizing
                icon_width, icon_height = icon_img.size
                aspect_ratio = icon_width / icon_height

                if icon_width > max_icon_width:
                    icon_width = max_icon_width
                    icon_height = int(icon_width / aspect_ratio)

                if icon_height > max_icon_height:
                    icon_height = max_icon_height
                    icon_width = int(icon_height * aspect_ratio)

                # Resize with high quality
                icon_img = icon_img.resize((icon_width, icon_height), Image.Resampling.LANCZOS)

                # Position the icon at the defined position
                icon_x = invitation.template.bottom_icon_x - (icon_img.width // 2)
                icon_y = invitation.template.bottom_icon_y - (icon_img.height // 2)

                # Paste the icon onto the template using alpha compositing
                if 'A' in icon_img.getbands():  # Check if image has alpha channel
                    template_img.paste(icon_img, (icon_x, icon_y), icon_img)
                else:
                    template_img.paste(icon_img, (icon_x, icon_y))

            except Exception as e:
                logger.error(f"Error adding bottom icon: {str(e)}")
                # Continue without the icon

        # Save the final image
        safe_name = ''.join(c if c.isalnum() else '_' for c in invitation.name)
        output_filename = f"{invitation.pk}_{safe_name}.png"
        output_path = f"invitations/{output_filename}"
        full_output_path = os.path.join(settings.MEDIA_ROOT, output_path)

        # Ensure directory exists
        os.makedirs(os.path.dirname(full_output_path), exist_ok=True)

        # Save the image with high quality
        template_img.save(full_output_path, format="PNG", optimize=True)
        logger.info(f"Saved invitation image to: {full_output_path}")

        # Update the invitation object with the final image
        invitation.final_image = output_path
        invitation.save(update_fields=['final_image'])

        return True, "Image generated successfully"

    except Exception as e:
        logger.error(f"Error generating invitation image: {str(e)}", exc_info=True)
        return False, f"Error generating invitation image: {str(e)}"


def delete_invitation_files(invitation):
    """
    Delete the image files associated with an invitation

    Args:
        invitation: Invitation model object
    """
    try:
        # Delete final image if it exists
        if invitation.final_image:
            image_path = os.path.join(settings.MEDIA_ROOT, str(invitation.final_image))
            if os.path.exists(image_path):
                os.remove(image_path)
                logger.info(f"Deleted invitation image: {image_path}")

        # Delete custom top image if it exists
        if invitation.custom_top_image:
            image_path = os.path.join(settings.MEDIA_ROOT, str(invitation.custom_top_image))
            if os.path.exists(image_path):
                os.remove(image_path)
                logger.info(f"Deleted custom top image: {image_path}")

        # Delete custom bottom image if it exists
        if invitation.custom_bottom_image:
            image_path = os.path.join(settings.MEDIA_ROOT, str(invitation.custom_bottom_image))
            if os.path.exists(image_path):
                os.remove(image_path)
                logger.info(f"Deleted custom bottom image: {image_path}")

    except Exception as e:
        logger.error(f"Error deleting invitation files: {str(e)}")
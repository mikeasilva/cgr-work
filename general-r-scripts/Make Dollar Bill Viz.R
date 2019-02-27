# Make Dollar Bill Viz
setwd(dirname(rstudioapi::getActiveDocumentContext()$path))
rm(list = ls())
library(magick)

# Define how you want the dollar bill split up.  The values do not need to sum to 100
parts <- c(70, 3, 11, 4, 5, 6, 1)

# Express the parts in percentage terms
scaled_parts <- parts / sum(parts)

space_between_slices_in_pixels <- 10

image <- image_read("one_dollar_bill.jpg")
width <- image_info(image)$width
height <- image_info(image)$height

spacer <- image_read("white.jpg")
spacer <- image_scale(spacer, paste0("x", height))
spacer <- image_crop(spacer, paste0(space_between_slices_in_pixels, "x", height))
used <- 0

for(p in scaled_parts){
  p_width <- round(p * width, 0)
  dim <- paste0(p_width, "x", height, "+", used)
  slice <- image_crop(image, dim)
  if(exists("final_image")){
    final_image <- append(final_image, c(slice, spacer))
  } else {
    final_image <- c(slice, spacer)
  }
  used <- used + p_width
}

final_image <- head(final_image, length(final_image)-1)
final_image <- image_append(final_image)

image_write(final_image, "dollar_bill_viz.jpg")
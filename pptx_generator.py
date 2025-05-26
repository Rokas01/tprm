from pptx import Presentation
from pptx.util import Pt

def apply_font(text_object):
    font = text_object.font
    font.name = 'Calibri'
    font.size = Pt(8)
    #font.bold = True
    #font.italic = None  # cause value to be inherited from theme




def add_slide(prs_object_input, layout_input, title_input):
    """Return slide newly added to `prs` using `layout` and having `title`."""

    slide_heading_from_call = title_input[0]
    requirement_text_from_call = title_input[1]
    summary_text_from_call = title_input[2]
    observation_text_from_call = title_input[3]
    
    slide = prs_object_input.slides.add_slide(layout_input)
    slide.shapes.title.text = slide_heading_from_call
    title_para = slide.shapes.title.text_frame.paragraphs[0]
    title_para.font.size = Pt(26)

    shapes = slide.shapes
    body_shape = shapes.placeholders[1]
    tf = body_shape.text_frame

    p0 = tf.add_paragraph()
    p0.text = 'Requirement'
    p0.font.size = Pt(12)
    p0.font.bold = True

    p1 = tf.add_paragraph()
    p1.text = requirement_text_from_call
    p1.font.size = Pt(9)
    p1.level = 1

    p2 = tf.add_paragraph()
    p2.text = "Summary"
    p2.level = 0
    p2.font.size = Pt(12)
    p2.font.bold = True

    p3 = tf.add_paragraph()
    p3.text = summary_text_from_call
    p3.font.size = Pt(9)
    p3.level = 1

    p4 = tf.add_paragraph()
    p4.text = "Emerging observations"
    p4.font.size = Pt(12)
    p4.font.bold = True
    p4.level = 0

    p5 = tf.add_paragraph()
    p5.text = observation_text_from_call
    p5.font.size = Pt(9)
    p5.level = 1
    
    return slide


def create_presentation_report_findings(title_text, subtitle_text, requirementsAndFindings, filename):

    prs = Presentation()
    title_slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(title_slide_layout)
    title = slide.shapes.title
    subtitle = slide.placeholders[1]

    title.text = title_text
    subtitle.text = subtitle_text

    for requirement in requirementsAndFindings:

        bullet_slide_layout = prs.slide_layouts[1]

        add_slide(prs, bullet_slide_layout, requirement)
 

    #prs.save(filename)

    return prs

#test_results = [["Article 21", "The measures referred to in paragraph 1 shall be based", "this is a summary", "not requested"], ["Article 22", "test text for the next article", "this is a summary", "not requested"]]

#create_presentation_report_findings("NIS2 compliance", "assessment report", test_results)


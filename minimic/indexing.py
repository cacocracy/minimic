import os


def make_rows(images):
    imgs = images
    tsets = []
    while len(imgs) > 0:
        tsets.append(imgs[:4])
        imgs = imgs[4:]
   
    res = ''
    for ts in tsets:
        row_html = ''.join([make_card(t) for t in ts])
        res += f'''
        <div class="w3-row-padding w3-margin-top">
        {row_html}
        </div>
        '''
    return res 

def make_card(img_path):
    html = f'''
    <div class="w3-col l3">
      <div class="w3-card w3-center w3-hover-shadow" style="height: 250px;">
        <img src="{img_path}" alt="none" class="w3-image" style="max-width: 95%; max-height:95%;">
        <div class="w3-container w3-center">
          <p>{img_path}</p>
        </div>
      </div>
    </div>
    '''
    return html

def gen_gallery_html(gallery_name):
    iexts = ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.svg']
    ifiles = [f for f in os.listdir(os.path.join(os.environ['MINIMIC_ARCHIVE'], gallery_name))
              if any([i in f.lower() for i in iexts])]
    imgs = make_rows(ifiles)
    start = ('<html><head>'
          '<meta name="viewport" content="width=device-width, initial-scale=1">'
          '<link rel="stylesheet" href="/w3.css"></head><body>')
    end = '<xscript src="/anim.js"></script></body></html>'
    htmld = f'{start}{imgs}{end}'
    with open(os.path.join(os.environ.get('MINIMIC_ARCHIVE'), gallery_name, 'index.html'), 'w') as htmlfile:
        htmlfile.write(htmld)


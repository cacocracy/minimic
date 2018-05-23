from typing import Any, Dict
import datetime
import logging
import random
import json
import time
import os
import re

from html import unescape
from pyquery import PyQuery as pq
import werkzeug
import urllib

from minimic.client import ClientSession
from minimic.exceptions import ParseError, MinimicException, SkippedAlbum


def download_image(client: ClientSession, image_url: str, target_dir: str,
                   referer_url: str, cnt: int = None,
                   force: bool = False) -> str:
    """Download an image and save to the target directory """

    if not os.path.isdir(target_dir):
        raise MinimicException(f"target_dir {target_dir} does not exist")
    
    image_dir = os.path.dirname(image_url)
    image_file = os.path.basename(image_url)
    enc_url = os.path.join(image_dir, urllib.parse.quote_plus(unescape(image_file)))
    logging.debug("Downloading image %s (%s)..." % (image_url, enc_url))

    secure_fname = werkzeug.utils.secure_filename(image_file)
    image_path = os.path.join(target_dir, secure_fname)
    if secure_fname in os.listdir(target_dir):
        if not force:
            logging.warning(f"{image_file} already downloaded "
                            f"in {target_dir}; skipping.")
            return None
        else:
            logging.warning(f"{image_file} already downloaded "
                            f"in {target_dir}; forcing refresh.")

    client.session.headers.update({'referer': referer_url})
    r = client.session.get(enc_url, stream=True, allow_redirects=True)
    with open(image_path, 'wb') as f:
        for chunk in r.iter_content(1024):
            f.write(chunk)
    logging.debug(f"Saved image {image_url} to {image_path}")
    return image_path


def fetch_album_data(client: ClientSession, album_url: str) -> Dict[str, Any]:
    """Fetch album info and return as dict; save nothing to disk """

    album_page = client.session.get(album_url, stream=True)
    album_page.raise_for_status()

    description = "Not found"
    try:
        S = pq(album_page.text)
        description = S('.about').text()
    except Exception as e:
        logging.warning(f"Cannot find description in {album_url}")

    likes_count = None
    try:
        likes_count = int(S('.likes_count').text().split(' ')[0])
    except Exception as e:
        logging.warning("Cannot find likes_count in {album_url}")
   
    locked_images_count = None
    try:
        r = re.search('([\d]+) locked images', S('.title-bar').text())
        if r:
            locked_images_count = int(r.group(1))
    except Exception as e:
        logging.warning("Cannot find locked_images_count on %s: %s" % (album_url, e))

    img_links = []
    profile_name, album_name = 'unknown', 'unknown'
    for line in album_page.text.splitlines(True):
        if '/profiles' in line and 'Private message' in line:
            profile_id = None
            try:
                # E.g.,  "/profiles/88468-user-name/messages/new"
                pidstr = line.split('href="')[1].split('" class=')[0]
                profile_id = int(pidstr.split('/')[2].split('-')[0])
            except Exception as e:
                logging.warning("Cannot get profile_id in {album_url}")

        if 'Full size' in line and 'max' in line:
            r = re.search(r'a href="([^"]*)".*title="', line)
            if r:
                img_links.append(r.groups()[0])
        elif '<title>' in line:
            line = line.replace('<title>', '').replace('</title>', '')
            tokens = line.split('|')
            album_name = tokens[0].strip()
            profile_name = tokens[-2].strip()

    # Remove duplicates
    img_links = list(set(img_links))
    profile_name = "".join([c for c in profile_name
                            if re.match(r'\w', c) or c == ' '])
    album_name = "".join([c for c in album_name
                          if re.match(r'\w', c) or c == ' '])

    return {'images': img_links,
            'profile_name': profile_name,
            'album_name': album_name,
            'description': description,
            'likes_count': likes_count,
            'locked_images_count': locked_images_count,
            'profile_id': profile_id}


def save_profile(client: ClientSession, profile_url: str, profile_id: int,
                 target_dir: str, force: bool = False) -> Dict[str, Any]:
    """Parse and then save the profile at the given url to disk """

    if not os.path.isdir(target_dir):
        raise MinimicException(f"target_dir {target_dir} does not exist")

    profile_page = client.session.get(profile_url, stream=True)
    profile_page.raise_for_status()
    
    galleries_page = client.session.get(f'{profile_url}/galleries',
                                        stream=True)
    galleries_page.raise_for_status()
    profile_info = {}

    S = pq(profile_page.text)
    profile_info['name'] = S('title').text().split('|')[0].strip()

    try:
        profile_info['intro'] = S('.small-9').text()
        profile_info['misc_info'] = S('.small-3').text()
    except Exception as e:
        logging.warning(f"{e}: Cannot find intro/misc_info for {profile_url}")

    try:
        flag = S('.flag img')
        profile_info['country_flag'] = flag.attr['src']
        profile_info['country'] = flag.attr['title']
        p = download_image(client,
                           profile_info['country_flag'],
                           target_dir,
                           profile_url)
        profile_info['country_flag_local'] = os.path.basename(p)
    except Exception as e:
        logging.warning(f"{e}: Cannot find flag/country on {profile_url}")

    profile_info['galleries'] = []
    try:
        G = pq(galleries_page.text)
        user_galleries = G('.user_gallery a')
        gallery_ids = [n for n in user_galleries
                       if 'galleries/' in n.attrib['href']]
        for g in gallery_ids:
            g_id = int(g.attrib['href'].split('/')[-1])
            profile_info['galleries'].append(g_id)
    except Exception as e:
        logging.warning(f'{e}: Cannot find galleires on {profile_url}')

    try:
        a = [l for l in profile_page.text.split('\n')
             if "class='avatar'" in l and 'src=' in l][:1]
        if len(a) != 1:
            raise ParseError('More than one avatar line')
        m = re.search('src="([^"]+)"', a[0])
        if m:
            profile_info['pic_url'] = m.groups()[0]
        else:
            raise ParseError('Cannot figure out avatar img')
        p = download_image(client, profile_info['pic_url'],
                           target_dir,
                           profile_url)
        profile_info['local_thumbnail'] = os.path.basename(p)
    except Exception as e:
        logging.warning(f"{e}: Cannot find profile pic on {profile_url}")

    profile_info['profile_id'] = profile_id
    with open(os.path.join(target_dir, 'info.json'), 'w') as info_json:
        info_json.write(json.dumps(profile_info, indent=2))

    logging.info("Saved profile info from {profile_url} "
                 "({profile_id}) to {info_json.name}")
    return profile_info


def save_album(client: ClientSession, album_url: str, target_dir: str,
               force: bool = False) -> Dict[str, Any]:
    """Save album info to disk and all contained images """

    album_data = fetch_album_data(client, album_url)
    album_id = [n for n in album_url.split('/') if n][-1]
    dirname = "p{}-a{}".format(album_data.get('profile_id'), album_id)
    album_path = os.path.join(target_dir, dirname)

    if os.path.exists(album_path):
        if force:
            logging.warning(f"{album_path} already exists; forcing refresh")
        else:
            raise SkippedAlbum(f"Skipping {album_path}")

    os.makedirs(album_path, exist_ok=True)
    metadata = {
        'timestamp': datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        'profile_name': album_data['profile_name'],
        'profile_id': album_data['profile_id'],
        'description': album_data['description'],
        'album_id': int(album_id),
        'album_name': album_data['album_name'],
        'likes_count': album_data['likes_count'],
        'locked_images_count': album_data['locked_images_count'],
        'images': len(album_data['images'])}

    with open(os.path.join(album_path, '00-Info.json'), 'w') \
        as info_file:
            info_file.write(json.dumps(metadata, sort_keys=True, indent=2))

    for i, image_path in enumerate(album_data['images']):
        try:
            logging.debug("Fetching image %s (%d/%d.. %d%%)" % 
                (image_path, i + 1, len(album_data['images']),
                 int(100.0 * (i + 1.0)/len(album_data['images']))))
            client.vprint('\r  {}% -- {} "{}" [{}] -- ({}/{}) -- ...{}'.format(
                int(100.0 * (i + 1)/len(album_data['images'])),
                werkzeug.utils.secure_filename(metadata.get('profile_name')),
                    werkzeug.utils.secure_filename(metadata.get('album_name')), 
                    metadata.get('album_id'),
                    (i+1),
                    len(album_data['images']), 
                    image_path[-12:]), 
                    end='',
                    flush=True)
            got = download_image(client, image_path, album_path, album_url)
            if got:
                time.sleep(1 + random.random()*2)
        except Exception as e:
            logging.error('Error downloading {}: {}'.format(image_path, e))
            time.sleep(0.5)

    return metadata

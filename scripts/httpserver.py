'''
internal_server.py

用于同一物理节点内，通过 http 实现 ipc；不适合用于跨物理节点的情况
'''
import logging
import sys
import time
import argparse

from threading import Lock
from flask import Flask
from flask import request
from flask import Response
from flask import jsonify
from flask import make_response
from inference import inference_process
from utils import log_error


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

log = logging.getLogger('hallo')
log.disabled = True

sys.stdout.reconfigure(encoding='utf-8')

busy_at = 0
busy_at_lock = Lock()


@app.route('/api/v1/hallo/generate', methods=['POST'])
def generate():
    '''
    GET /api/v1/hallo/generate hallo生成接口
    Input JSON:
    {
        'source_image': ',
        'driving_audio': '',
        'pose_weight': 1.0,
        'face_weight': 1.0,
        'lip_weight': 1.0,
        'face_expand_ratio': 1.2,
        'config': 'configs/inference/default.yaml',
        'checkpoint': null,
        'output': 'cache/{file_name_nano_id}.mp4'
    }
    Output: 200 with no content
    '''
    try:
        busy_at_lock.acquire()
        if busy_at > 0:
            busy_at_lock.release()
            return jsonify({"error": "busy"}), 429
        else:
            busy_at = int(time.time())
            busy_at_lock.release()

        req_body = request.json

        # param check
        if 'source_image' not in req_body:
            return jsonify({"error": "source_image is required"})
        if 'driving_image' not in req_body:
            return jsonify({"error": "driving_image is required"})
        if 'output' not in req_body:
            return jsonify({"error": "output is required"})
        
        # param transform
        args = argparse.Namespace(
            source_image=req_body['source_image'],
            driving_audio=req_body['driving_audio'],
            output=req_body['output'],
            pose_weight=req_body.get('pose_weight', 1.0),
            face_weight=req_body.get('face_weight', 1.0),
            lip_weight=req_body.get('lip_weight', 1.0),
            face_expand_ratio=req_body.get('face_expand_ratio', 1.2),
            config=req_body.get('config', 'configs/inference/default.yaml'),
            checkpoint=req_body.get('checkpoint', None),
        )

        # do infer
        inference_process(args)
        return Response(status=200)
    except Exception as e:
        log_error("hallo generate error: %s", e)
        return make_response(f"Error: {str(e)}", 500)
    finally:
        # reset busy_at timestamp
        busy_at_lock.acquire()
        busy_at = 0
        busy_at_lock.release()


@app.route('/health', methods=['GET'])
def health():
    '''
    GET /health 健康检查接口
    '''
    return "OK"


@app.route('/status', methods=['GET'])
def status():
    '''
    GET /status 状态接口 
    '''
    busy_at_lock.acquire()
    rsp = {"busy_at": busy_at}
    busy_at_lock.release()
    return rsp


if __name__ == '__main__':
    app.run(debug=False, port='9000')

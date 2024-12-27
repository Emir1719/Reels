from flask import Blueprint, jsonify, request
from reels_transcript import ReelsTranscript
from service.translate import Translate

reels = Blueprint("reels", __name__, url_prefix="/reels")
reels_transcript = ReelsTranscript()
translate = Translate()


@reels.route("/", methods=["POST"])
def get_transcript():
    link = request.json.get("link")
    
    if not link:
        return jsonify({"message": "Link boş olamaz", "data": None}), 400
    
    try:
        text = reels_transcript.get(link)
        
        if text:
            return jsonify({"message": "Başarılı", "data": text}), 200
        else:
            return jsonify({"message": "Bu reelsin metnine erişilemedi", "data": None}), 400
    except ValueError as e:
        return jsonify({"message": e, "data": None}), 400


@reels.route("/tr", methods=["POST"])
def get_transcript_with_turkish():
    link = request.json.get("link")
    
    if not link:
        return jsonify({"message": "Link boş olamaz", "data": None}), 400
    
    try:
        text = reels_transcript.get(link)
        translated_text = translate.translateWithGoogle(text) 
        
        if text and translated_text:
            return jsonify({"message": "Başarılı", "data": translated_text, "original": text}), 200
        else:
            return jsonify({"message": "Bu reelsin metnine erişilemedi", "data": None}), 400
    except ValueError as e:
        return jsonify({"message": e, "data": None}), 400

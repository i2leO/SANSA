"""Idempotently import the approved 25-item knowledge-media bundle."""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import SessionLocal
from app.models import KnowledgePost, User


PDF_TITLES = [
    "6 วิธีเพิ่มความอยากอาหารให้ผู้สูงอายุ",
    "อาหารแลกเปลี่ยน หมวดข้าวและแป้ง",
    "อาหารแลกเปลี่ยน หมวดเนื้อสัตว์",
    "อาหารแลกเปลี่ยน หมวดผัก",
    "อาหารแลกเปลี่ยน หมวดผลไม้",
    "อาหารแลกเปลี่ยน หมวดนม",
    "อาหารแลกเปลี่ยน หมวดน้ำมัน",
    "เลือกน้ำมันให้เป๊ะ เหมาะกับเมนู",
    "ลดน้ำหนักอย่างปลอดภัย",
    "สูงวัยห่างไกลกระดูกพรุน",
    "ธงโภชนาการผู้สูงอายุ",
    "ผู้สูงอายุ กินอะไร หัวใจดี๊ดี",
    "โภชนบัญญัติ 9 ประการ สำหรับผู้สูงอายุ",
    "หลักการจัดอาหารผู้สูงอายุ",
    "อาหารลดความเสี่ยงสมองเสื่อม",
]

MISSION_TITLES = [
    "MISSION วันนี้: ดื่มน้ำเพิ่ม 1 แก้ว",
    "MISSION วันนี้: ลดข้าว แต่ต้องอิ่ม",
    "MISSION วันนี้: ลดหวาน 1 ระดับ",
    "MISSION วันนี้: ผลไม้พอดี 1-2 ส่วน",
    "MISSION วันนี้: เพิ่มผัก 1 อย่าง",
    "MISSION วันนี้: เพิ่มสีของอาหาร 1 สี",
    "MISSION วันนี้: เพิ่มโปรตีน 1 อย่าง",
    "MISSION วันนี้: ลดน้ำมันหรือทอด 1 มื้อ",
    "MISSION วันนี้: เพิ่มข้าว-แป้ง 1 มื้อ",
    "MISSION วันนี้: เพิ่มแคลเซียม",
]


def records():
    for index, title in enumerate(PDF_TITLES, 1):
        number = f"{index:02d}"
        yield dict(
            slug=f"nutrition-60plus-{number}", title=title,
            summary="อินโฟกราฟิกความรู้ด้านอาหารและโภชนาการสำหรับผู้สูงอายุ",
            category="กินดีวัย 60+", tags="ผู้สูงอายุ,โภชนาการ,อินโฟกราฟิก",
            featured_image_path=f"/knowledge-media/nutrition-{number}.webp",
            media_path=f"/knowledge-media/nutrition-{number}.pdf", media_type="pdf",
            display_order=index,
        )
    for index, title in enumerate(MISSION_TITLES, 1):
        number = f"{index:02d}"
        yield dict(
            slug=f"nutrition-mission-{number}", title=title,
            summary="ภารกิจโภชนาการง่าย ๆ ที่นำไปทำได้ในชีวิตประจำวัน",
            category="MISSION", tags="ภารกิจ,ผู้สูงอายุ,โภชนาการ",
            featured_image_path=f"/knowledge-media/mission-{number}.webp",
            media_path=f"/knowledge-media/mission-{number}.webp", media_type="image",
            display_order=100 + index,
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write changes; default is dry-run")
    args = parser.parse_args()
    db = SessionLocal()
    try:
        creator = db.query(User).filter(User.role == "admin", User.is_active == True).order_by(User.id).first()
        if not creator:
            raise RuntimeError("No active admin account exists")
        created = updated = 0
        for data in records():
            post = db.query(KnowledgePost).filter(KnowledgePost.slug == data["slug"]).first()
            if post is None:
                post = KnowledgePost(slug=data["slug"], created_by=creator.id)
                db.add(post)
                created += 1
            else:
                updated += 1
            for key, value in data.items():
                setattr(post, key, value)
            post.content = None
            post.is_published = True
            post.is_deleted = False
        if args.apply:
            db.commit()
        else:
            db.rollback()
        print({"mode": "apply" if args.apply else "dry-run", "created": created,
               "updated": updated, "total": created + updated})
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

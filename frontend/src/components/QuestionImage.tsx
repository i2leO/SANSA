const images: Record<number,string> = {
  5: '1.ass_meal.jpg',
  6: '2. ass_intake_.jpg',
  7: '3. ass_type.png',
  8: '4. ass_rice_starch.jpg',
  9: '5. ass_meat_egg.jpg',
  10: '6. ass_milk.jpg',
  11: '7. ass_fruit.jpg',
  12: '8. ass_veget.jpg',
  13: '9. ass_water.jpg',
  14: '10. ass_sweetdrink.jpg',
  15: '11. ass_cook.png',
  16: '12. ass_oil.jpg',
};

export default function QuestionImage({number,alt}:{number:number;alt:string}) {
  const filename=images[number];
  if(!filename)return null;
  return <img className="sansa-question-image" src={`/question-images/${encodeURIComponent(filename)}`} alt={`ภาพประกอบคำถามข้อ ${number}: ${alt}`} loading="lazy" />;
}

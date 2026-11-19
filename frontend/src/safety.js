// Exact, deterministic matching only. This is not a risk assessment.
export function normalize(text){return text.toLocaleLowerCase().normalize('NFKD').replace(/\p{M}/gu,'');}
export function matchesCrisis(text,keywords){
 const value=normalize(text);
 return Object.values(keywords||{}).flat().some(phrase=>{
  const escaped=normalize(phrase).replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
  return new RegExp('(?<![\\p{L}\\p{N}_])'+escaped+'(?![\\p{L}\\p{N}_])','u').test(value);
 });
}

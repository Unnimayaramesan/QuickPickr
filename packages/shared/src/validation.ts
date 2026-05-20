const PINCODE_RE = /^[1-9][0-9]{5}$/;

export function validatePincode(pincode: string): boolean {
  return PINCODE_RE.test(pincode.trim());
}

export function validateQuery(query: string): boolean {
  const q = query.trim();
  return q.length >= 2 && q.length <= 120;
}

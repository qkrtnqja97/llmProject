export interface User {
  empId: string;
  name?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

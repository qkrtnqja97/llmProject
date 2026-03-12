// src/shared/types/declarations.d.ts

// .module.css 파일에 대한 타입 정의
declare module "*.module.css" {
  const classes: { [key: string]: string };
  export default classes;
}

// (참고) 이미지 파일 등도 여기서 미리 정의해두면 편리합니다.
declare module "*.png";
declare module "*.jpg";
declare module "*.svg";

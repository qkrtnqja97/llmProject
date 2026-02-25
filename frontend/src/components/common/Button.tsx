import React from "react";
import styles from "./Button.module.css";

interface Props extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary";
}

export const Button: React.FC<Props> = ({
  variant = "primary",
  children,
  ...props
}) => (
  <button className={`${styles.btn} ${styles[variant]}`} {...props}>
    {children}
  </button>
);

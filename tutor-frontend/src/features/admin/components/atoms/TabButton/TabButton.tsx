import clsx             from "clsx";
import { type ButtonHTMLAttributes } from "react";
import styles           from "./TabButton.module.css";

interface TabButtonProps
  extends Omit<ButtonHTMLAttributes<HTMLButtonElement>, "type" | "onClick"> {
  active:   boolean;
  label:    string;
  onClick:  () => void;
  controls: string;
  id:       string;
}

const TabButton = ({
  active,
  label,
  onClick,
  id,
  controls,
  ...rest
}: TabButtonProps) => (
  <button
    {...rest}
    id={id}
    role="tab"
    aria-controls={controls}
    aria-selected={active}
    className={clsx(styles.btn, active && styles.active)}
    onClick={onClick}
    type="button"
  >
    {label}
  </button>
);

export default TabButton;

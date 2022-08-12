import React from "react"
import { StyledWidgetLabel } from "./styled-components"

export interface LabelProps {
  // Label body text. If nullsy, WidgetLabel won't show. But if empty string it will.
  label?: string | null

  // Used to specify other elements that should go inside the label container, like a help icon.
  children?: React.ReactNode

  // Used to specify whether widget disabled or enabled.
  disabled?: boolean | null
}

export function WidgetLabel({
  label,
  children,
  disabled,
}: LabelProps): React.ReactElement {
  if (label == null) {
    return <></>
  }

  return (
    <StyledWidgetLabel disabled={disabled}>
      {label}
      {children}
    </StyledWidgetLabel>
  )
}

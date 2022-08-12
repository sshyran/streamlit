import styled from "@emotion/styled"

export interface StyledWidgetProps {
  disabled?: boolean | null
}

export const StyledWidgetLabel = styled.label<StyledWidgetProps>(
  ({ disabled, theme }) => ({
    fontSize: theme.fontSizes.sm,
    color: disabled ? theme.colors.fadedText40 : theme.colors.bodyText,
    marginBottom: theme.spacing.sm,
    height: "auto",
    minHeight: theme.fontSizes.xl,
    verticalAlign: "middle",
    display: "flex",
    flexDirection: "row",
    alignItems: "center",
  })
)

export const StyledWidgetLabelHelp = styled.div(() => ({
  display: "flex",
  flexDirection: "row",
  justifyContent: "flex-end",
  flex: 1,
}))

export const StyledWidgetInstructions = styled.div(({ theme }) => ({
  fontSize: theme.fontSizes.twoSm,
  color: theme.colors.fadedText60,
  margin: theme.spacing.none,
  textAlign: "right",
  position: "absolute",
  bottom: 0,
  right: theme.spacing.halfSmFont,
}))

export const StyledWidgetLabelHelpInline = styled.label(({ theme }) => ({
  marginLeft: theme.spacing.xs,
  position: "relative",
  display: "flex",
  flexDirection: "row",
}))

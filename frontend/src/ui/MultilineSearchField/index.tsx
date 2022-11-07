import { ClearButton, Root, TextArea } from "./style"
import ClearIcon from "@material-ui/icons/Clear";



export const MultilineSearchField = () => {

  return (
    <Root>
      <TextArea
        height={200}
        placeholder="Enter paper's title, abstract or any other text related to this paper"
      >
        asdasd
      </TextArea>
      <ClearButton>
        <ClearIcon />
      </ClearButton>
    </Root>
  )
}

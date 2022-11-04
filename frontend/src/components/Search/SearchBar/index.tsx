
import Bar from "material-ui-search-bar";
import { OnSearchStateChange } from "../../../types/search";

interface Props {
  index: number;
  text: string;
  onSearchStateChange: OnSearchStateChange
}

export const SearchBar = ({index, text, onSearchStateChange}: Props) => {

  return (
    <div>
      <Bar
        placeholder='Search'
        value={text}
        onChange={(newValue) => onSearchStateChange(index, newValue)}
        // onRequestSearch={() => queryPapers()}
        style={{
          margin: '20px 0',
        }}
      />
    </div>
  )
}

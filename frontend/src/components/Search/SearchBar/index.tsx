
import Bar from "material-ui-search-bar";
import ClearIcon from "@material-ui/icons/Clear";
import grey from '@material-ui/core/colors/grey';
import { OnSearchItemRemove, OnSearchStateChange } from "../../../types/search";

interface Props {
  index: number;
  text: string;
  onSearchStateChange: OnSearchStateChange;
  isRemovalEnabled: boolean;
  onSearchItemRemove: OnSearchItemRemove;
}

export const SearchBar = ({
  index,
  text,
  onSearchStateChange,
  isRemovalEnabled,
  onSearchItemRemove
}: Props) => {
  console.log('isRemovalEnabledisRemovalEnabled', isRemovalEnabled)

  const handleItemRemove = () => isRemovalEnabled && onSearchItemRemove(index)
  return (
    <div>
      <Bar
        placeholder='Search'
        value={text}
        onChange={(newValue) => onSearchStateChange(index, newValue)}
        searchIcon={<ClearIcon style={{ color: grey[500] }} />}
        onRequestSearch={handleItemRemove} // allow only to delete now
        onCancelSearch={handleItemRemove}

        style={{
          margin: '20px 0',
        }}
      />
    </div>
  )
}

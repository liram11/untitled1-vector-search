import { Link } from "@mui/material"

export const SuggestedCategories = ({options, onClick}: {options: string[], onClick: () => void}) => {
  if (options.length === 0) return <></>

  return (
    <div className="pt-2">
      We found suggested categories for your query: <br /> {options.join(', ')} <br />
      <Link component="button" underline="hover" onClick={onClick}>Apply them</Link>
    </div>
  )
}


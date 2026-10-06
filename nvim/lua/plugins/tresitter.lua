return {
	"nvim-treesitter/nvim-treesitter",
	lazy = false,
	build = ":TSUpdate",
	config = function()
		local treesitter = require("nvim-treesitter")
		treesitter.install({ "lua", "python", "json", "html", "css", "bash", "yaml", "c", "cpp", "sql", "java" })

		vim.api.nvim_create_autocmd("FileType", {
			callback = function(args)
				local lang = vim.treesitter.language.get_lang(vim.bo[args.buf].filetype)
				if not lang or not vim.list_contains(treesitter.get_available(), lang) then return end
				treesitter.install({ lang }):await(function(err, success)
					if err or not success or not vim.api.nvim_buf_is_valid(args.buf) then return end
					if pcall(vim.treesitter.start, args.buf) then
						vim.bo[args.buf].indentexpr = "v:lua.require'nvim-treesitter'.indentexpr()"
					end
				end)
			end,
		})
	end,
}

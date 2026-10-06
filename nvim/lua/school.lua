local M = {}

function M.lazy_opts()
	local spec = {}
	for _, name in ipairs({
		"catppuccin", "telescope", "mini", "oil", "gitsigns", "which-key",
		"lua-line", "indent-blankline", "neoscroll", "visimatch", "noice-line",
		"nvim-lspconfig", "osc52", "vim-tmux-navigator", "surround",
	}) do
		spec[#spec + 1] = require("plugins." .. name)
	end
	spec[#spec + 1] = {
		"nvim-treesitter/nvim-treesitter",
		lazy = false,
		config = function()
			require("nvim-treesitter").setup({ install_dir = vim.env.SCHOOL_NVIM_PARSERS })
			vim.api.nvim_create_autocmd("FileType", {
				pattern = { "c", "cpp", "lua", "sh", "bash" },
				callback = function(args)
					vim.treesitter.start(args.buf)
					vim.bo[args.buf].indentexpr = "v:lua.require'nvim-treesitter'.indentexpr()"
				end,
			})
		end,
	}
	return {
		spec = spec,
		root = vim.env.SCHOOL_NVIM_PLUGINS,
		lockfile = vim.env.MY_VIM_ENV .. "/school/lazy-lock.json",
		install = { missing = false },
		checker = { enabled = false },
		change_detection = { enabled = false },
	}
end

function M.setup()
	-- These daily-profile actions need tools deliberately omitted at school.
	vim.keymap.del("n", "<M-m>")
	vim.keymap.del("n", "<M-p>")
	vim.keymap.set("n", "<M-c>", function()
		vim.cmd("write")
		local path = vim.api.nvim_buf_get_name(0)
		local compiler = vim.bo.filetype == "cpp" and "g++" or "gcc"
		local binary = vim.fn.fnamemodify(path, ":r")
		local command = compiler .. " " .. vim.fn.shellescape(path)
			.. " -o " .. vim.fn.shellescape(binary) .. " && " .. vim.fn.shellescape(binary)
		vim.cmd("Floaterminal")
		vim.fn.chansend(vim.bo.channel, command .. "\n")
	end, { desc = "Compile and run current C/C++ file" })
end

return M

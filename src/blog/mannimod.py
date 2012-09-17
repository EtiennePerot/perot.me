from pygments.style import Style
from pygments.token import Keyword, Name, Comment, String, Error, Number, Operator, Generic, Whitespace
from pygments.styles.manni import ManniStyle

class ManniStyle_mod(Style):
	background_color = ManniStyle.background_color
	styles = {
		Whitespace:         ManniStyle.styles[Whitespace],
		Comment:            'italic #30306F',
		Comment.Preproc:    ManniStyle.styles[Comment.Preproc],
		Comment.Special:    ManniStyle.styles[Comment.Special],

		Keyword:            ManniStyle.styles[Keyword],
		Keyword.Pseudo:     ManniStyle.styles[Keyword.Pseudo],
		Keyword.Type:       ManniStyle.styles[Keyword.Type],

		Operator:           ManniStyle.styles[Operator],
		Operator.Word:      ManniStyle.styles[Operator.Word],

		Name.Builtin:       ManniStyle.styles[Name.Builtin],
		Name.Function:      ManniStyle.styles[Name.Function],
		Name.Class:         ManniStyle.styles[Name.Class],
		Name.Namespace:     ManniStyle.styles[Name.Namespace],
		Name.Exception:     ManniStyle.styles[Name.Exception],
		Name.Variable:      '#006C6C',
		Name.Constant:      ManniStyle.styles[Name.Constant],
		Name.Label:         ManniStyle.styles[Name.Label],
		Name.Entity:        ManniStyle.styles[Name.Entity],
		Name.Attribute:     ManniStyle.styles[Name.Attribute],
		Name.Tag:           ManniStyle.styles[Name.Tag],
		Name.Decorator:     ManniStyle.styles[Name.Decorator],

		String:             ManniStyle.styles[String],
		String.Doc:         ManniStyle.styles[String.Doc],
		String.Interpol:    ManniStyle.styles[String.Interpol],
		String.Escape:      ManniStyle.styles[String.Escape],
		String.Regex:       ManniStyle.styles[String.Regex],
		String.Symbol:      ManniStyle.styles[String.Symbol],
		String.Other:       ManniStyle.styles[String.Other],

		Number:             ManniStyle.styles[Number],

		Generic.Heading:    ManniStyle.styles[Generic.Heading],
		Generic.Subheading: ManniStyle.styles[Generic.Subheading],
		Generic.Deleted:    ManniStyle.styles[Generic.Deleted],
		Generic.Inserted:   ManniStyle.styles[Generic.Inserted],
		Generic.Error:      ManniStyle.styles[Generic.Error],
		Generic.Emph:       ManniStyle.styles[Generic.Emph],
		Generic.Strong:     ManniStyle.styles[Generic.Strong],
		Generic.Prompt:     'bold #30609F',
		Generic.Output:     '#303333',
		Generic.Traceback:  ManniStyle.styles[Generic.Traceback],

		Error:              ManniStyle.styles[Error],
	}

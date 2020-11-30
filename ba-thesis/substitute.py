import pystache
import yaml
import argparse
import re
 
def ec(u):
	print(u)
	return u
	 
def render(text, variables):
        result_text = pystache.render(text, variables, escape = ec, string_encoding = "utf8")
        if result_text.count("{{"):
            raise ConfigurationException("Unresolved variable")
        print(result_text)
        return result_text 

def replace_png_width_pdf(text):
	return re.sub(r'\((.+).png\)', r'(\1.pdf)', text)
        

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Replace {{values}}.')
	parser.add_argument('-y', '--yaml', type=str,
		                help='YAML file including values.', required=True)
	parser.add_argument('-t', '--template', type=str,
		                help='Template file.', required=True)
	parser.add_argument('-o', '--output', type=str,
		                help='Output file.', required=False)

	args = parser.parse_args()

	with open(args.yaml, 'r') as f:
		variables = yaml.safe_load(f)
		
	with open(args.template, 'r') as f:
		text = f.read()

	out = render(text, variables)
	out = replace_png_width_pdf(out)

	if args.output != None:
		with open(args.output, "w") as f:
			f.write(out)
	else:
		print(out)


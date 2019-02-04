import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.Properties;

import SPM.Parser;
import edu.stanford.nlp.ling.CoreAnnotations;
import edu.stanford.nlp.ling.CoreAnnotations.SentencesAnnotation;
import edu.stanford.nlp.ling.CoreAnnotations.TokensAnnotation;
import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.parser.lexparser.LexicalizedParser;
import edu.stanford.nlp.pipeline.Annotation;
import edu.stanford.nlp.pipeline.StanfordCoreNLP;
import edu.stanford.nlp.simple.Sentence;
import edu.stanford.nlp.trees.GrammaticalStructure;
import edu.stanford.nlp.trees.GrammaticalStructureFactory;
import edu.stanford.nlp.trees.Tree;
import edu.stanford.nlp.trees.TreebankLanguagePack;
import edu.stanford.nlp.trees.TypedDependency;
import edu.stanford.nlp.util.CoreMap;

public class CorpusPreprocessing {
	private final static String PCG_MODEL = "edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz";

	public final static LexicalizedParser parser2 = LexicalizedParser
			.loadModel(PCG_MODEL);

	public Tree parse(String str) {
		Properties cfg;
		cfg = new Properties();
		cfg.put("annotators", "tokenize, ssplit, pos, lemma");
		StanfordCoreNLP pipeline = new StanfordCoreNLP(cfg);
		Annotation document = new Annotation(str);
		pipeline.annotate(document);
		List<CoreMap> sentences = document.get(SentencesAnnotation.class);
		CoreMap sentence = null;
		int max = 0;
		for (CoreMap sent : sentences) {
			List<CoreLabel> tokens2 = sent.get(TokensAnnotation.class);
			if (tokens2.size() > max) {
				max = tokens2.size();
				sentence = sent;
			}
		}
		List<CoreLabel> tokens = sentence.get(TokensAnnotation.class);
		Tree tree = parser2.apply(tokens);
		return tree;
	}

	public Collection<TypedDependency> getDependancy(Tree tree) {
		TreebankLanguagePack tlp = parser2.getOp().langpack();
		GrammaticalStructureFactory gsf = tlp.grammaticalStructureFactory();
		GrammaticalStructure gs = gsf.newGrammaticalStructure(tree);
		Collection<TypedDependency> tdl = gs.typedDependenciesCollapsed();
		return tdl;
	}

	public String lemmatize(String word) {
		Sentence sentence = new Sentence(word);
		String lemma = sentence.lemmas().get(0);
		return lemma;
	}

	public List<String> NounPhrasesHead(List<String> NPs) {
		List<String> heads = new ArrayList<String>();
		for (String NP : NPs) {
			heads.add(NPHead(NP));
		}
		return heads;
	}

	public String NPHead(String NP) {
		if (NP.split(" ").length == 1) {
			return NP;
		}
		int nn = 0;
		Properties props = new Properties();
		props.setProperty("annotators", "tokenize, ssplit, pos");
		StanfordCoreNLP pipeline = new StanfordCoreNLP(props);
		Annotation annotation = new Annotation(NP);
		pipeline.annotate(annotation);
		List<CoreMap> sentences = annotation
				.get(CoreAnnotations.SentencesAnnotation.class);
		List<String> words = new ArrayList<String>();
		List<String> tags = new ArrayList<String>();
		for (CoreMap sentence : sentences) {
			for (CoreLabel token : sentence
					.get(CoreAnnotations.TokensAnnotation.class)) {
				String word = token.get(CoreAnnotations.TextAnnotation.class);
				words.add(word);
				String pos = token
						.get(CoreAnnotations.PartOfSpeechAnnotation.class);
				tags.add(pos);
			}
		}
		boolean conjFlag = false;
		if (tags.contains("CC")) {
			conjFlag = true;
		}
		String word = "";
		for (int i = 0; i < tags.size(); i++) {
			if (tags.get(i).equals("IN")
					|| (conjFlag && tags.get(i).equals(","))
					|| (conjFlag && tags.get(i).equals("CC"))) {
				break;
			}
			if (tags.get(i).contains("NN")) {
				word = words.get(i);
				nn++;
			}
		}
		if (nn == 1)
			return word;
		return word;
	}

	public void nounPhrases(Tree tree, List<String> NPs) {
		if (tree == null)
			return;
		if (tree.getLeaves().size() == 1
				&& (tree.value().trim().equals("NP") || tree.value().trim()
						.contains("NN"))) {
			NPs.add(tree.getLeaves().get(0).toString());
			return;
		}
		if (tree.value().trim().equals("NP") && tree.getLeaves().size() < 10) {
			System.out.println(tree.toString());
			int NPFlag = tree.toString().replace("NNP", "NN").split("NP").length;
			String NP = "";
			for (Tree tree2 : tree.getLeaves()) {
				NP += tree2.toString() + " ";
			}
			if (NPFlag == 2 && !NP.trim().contains("such as")
					&& !NP.trim().contains("including")
					&& !NP.trim().contains("especially")
					&& !NP.trim().contains("and") && !NP.trim().contains("or")
					&& !NP.trim().contains("other") && !NP.trim().contains(",")) {

				NPs.add(NP.trim());
			}
		}

		for (Tree t : tree.children()) {
			nounPhrases(t, NPs);
		}
	}

	public List<String> distinctNounPhrases(Tree tree) {
		ArrayList<String> NPs = new ArrayList<String>();
		nounPhrases(tree, NPs);
		List<String> li = NPs;
		List<String> newli = new ArrayList<String>();
		for (String NP : NPs) {
			boolean flag = true;
			for (String e : li) {
				e = " " + e + " ";
				if (!e.equals(" " + NP.trim() + " ")
						&& e.contains(" " + NP.trim() + " ")) {
					// System.out.println(e);
					// System.out.println(NP);
					flag = false;
					break;
				}
			}
			if (flag) {
				newli.add(NP.trim());
			}
		}
		return newli;
	}

	public List<String> getHypers(String annSent) {
		List<String> hypers = new ArrayList<String>();
		for (String word : annSent.replace(".", "").split(" ")) {
			if (word.contains("_hyper")) {
				// word = word.split("#")[1];
				hypers.add(NPHead(word.replace("_hyper", "").replace("_", " ")));
			}
		}
		return hypers;
	}

	public List<String> getHypos(String annSent) {
		List<String> hypos = new ArrayList<String>();
		for (String word : annSent.replace(".", "").split(" ")) {
			if (word.contains("_hypo")) {
				// word = word.split("#")[1];
				hypos.add(NPHead(word.replace("_hypo", "").replace("_", " ")));
			}
		}
		return hypos;
	}

	public List<String> getPathFromDPar(String annSent) {
		List<String> path = new ArrayList<String>();
		List<String> hypers = getHypers(annSent);
		List<String> hypos = getHypos(annSent);
		// System.out.println(hypers);
		// System.out.println(hypos);
		String line = annSent.replace("_hypo", "").replace("_hyper", "")
				.replace("_np", "").replace("_", " ").replace("#", "");
		// System.out.println(annSent);
		// System.out.println(line);
		Parser parser = new Parser();
		TreebankLanguagePack tlp = parser.parser2.getOp().langpack();
		GrammaticalStructureFactory gsf = tlp.grammaticalStructureFactory();
		Tree tree = parser.parse(line);
		List<String> NPs = new ArrayList<String>();
		NPs = distinctNounPhrases(tree);
		// System.out.println(tree);
		List<String> heads = NounPhrasesHead(NPs);
		// System.out.println(NPs);
		// System.out.println(heads);
		// System.out.println(hypers);
		GrammaticalStructure gs = gsf.newGrammaticalStructure(tree);
		Collection<TypedDependency> tdl = gs.typedDependenciesCollapsed();
		System.out.println(tdl);
		boolean isHyper = false;
		boolean isHypo = false;
		int i = 0;
		for (TypedDependency td : tdl) {
			if (i > NPs.size() - 1)
				i = NPs.size() - 1;
			String np = NPs.get(i);
			String npHead = heads.get(i);
			String word = td.dep().word();
			int depIndex = td.dep().index();
			int headIndex = td.gov().index();
			String rel = td.reln().toString();
			String lemma = td.dep().lemma();
			String tag = td.dep().tag();
			String headWord = td.gov().word();
			if (hypers.contains(headWord))
				headWord = "hyper";
			else if (hypos.contains(headWord))
				headWord = "hypo";
			// System.out.println(lemma);
			String direction = "";
			if (depIndex < headIndex)
				direction = "-->";
			else
				direction = "<--";
			String str2 = "";
			boolean flag = false;
			String[] npWords = np.split(" ");
			String lastNPWord = npWords[npWords.length - 1];
			if ((" " + np + " ").contains(" " + word + " ")) {
				if (word.equals(npHead)) {
					if (hypers.contains(word)) {
						isHyper = true;
						str2 = "(" + np.replace(" ", "_")
								+ "_label, NP, hyper, " + lemma + "_lemma, "
								+ tag + ", " + rel + direction + ", "
								+ headWord + "_dep)";
					} else if (hypos.contains(word)) {
						isHypo = true;
						str2 = "(" + np.replace(" ", "_")
								+ "_label, NP, hypo, " + lemma + "_lemma, "
								+ tag + ", " + rel + direction + ", "
								+ headWord + "_dep)";
					} else {
						str2 = "(" + np.replace(" ", "_") + "_label, NP, "
								+ lemma + "_lemma, " + tag + ", " + rel
								+ direction + ", " + headWord + "_dep)";
					}
					path.add(str2);
				}
				if (word.equals(lastNPWord))
					i++;
			} else {
				if (hypers.contains(word)) {
					isHyper = true;
					str2 = "(" + word + "_label, hyper, " + lemma + "_lemma, "
							+ tag + ", " + rel + direction + ", " + headWord
							+ "_dep)";
				} else if (hypos.contains(word)) {
					isHypo = true;
					str2 = "(" + word + "_label, hypo, " + lemma + "_lemma, "
							+ tag + ", " + rel + direction + ", " + headWord
							+ "_dep)";
				} else {
					str2 = "(" + word + "_label, " + lemma + "_lemma, " + tag
							+ ", " + rel + direction + ", " + headWord
							+ "_dep)";
				}
				path.add(str2);
			}
		}
		return path;
	}

	public StringBuilder sentenceParsing(String annSent) {
		StringBuilder strB = new StringBuilder("");
		strB.append("<s>\n");
		List<String> hypers = getHypers(annSent);
		List<String> hypos = getHypos(annSent);
		String line = annSent.replace("_hypo", "").replace("_hyper", "")
				.replace("_", " ");
		Parser parser = new Parser();
		TreebankLanguagePack tlp = parser.parser2.getOp().langpack();
		GrammaticalStructureFactory gsf = tlp.grammaticalStructureFactory();
		Tree tree = parser.parse(line);
		List<String> NPs = new ArrayList<String>();
		NPs = distinctNounPhrases(tree);
		List<String> heads = NounPhrasesHead(NPs);
		GrammaticalStructure gs = gsf.newGrammaticalStructure(tree);
		Collection<TypedDependency> tdl = gs.typedDependenciesCollapsed();
		int i = 0;
		boolean NPFlag = false;
		for (TypedDependency td : tdl) {
			if (i > NPs.size() - 1)
				i = NPs.size() - 1;
			String np = NPs.get(i);
			String npHead = heads.get(i);
			String word = td.dep().word();
			int depIndex = td.dep().index();
			int headIndex = td.gov().index();
			String rel = td.reln().toString();
			String lemma = td.dep().lemma();
			String tag = td.dep().tag();
			String headWord = td.gov().word();
			if (hypers.contains(headWord))
				headWord = "hyper";
			else if (hypos.contains(headWord))
				headWord = "hypo";
			String direction = "";
			if (depIndex < headIndex)
				direction = "-->";
			else
				direction = "<--";
			String str2 = "";
			boolean flag = false;
			String[] npWords = np.split(" ");
			String hTag = "None";
			String lastNPWord = npWords[npWords.length - 1];
			if ((" " + np + " ").contains(" " + word + " ")) {
				if (!NPFlag) {
					strB.append("<NP>\n");
					NPFlag = true;
				}
				if (word.equals(npHead)) {
					strB.append("<root>\n");
					if (hypers.contains(word)) {
						hTag = "hyper";
					} else if (hypos.contains(word)) {
						hTag = "hypo";
					}
					String li = word + "\t" + lemma + "\t" + tag + "\t"
							+ depIndex + "\t" + headWord + "\t" + headIndex
							+ "\t" + rel + direction + "\t" + hTag + "\n";
					strB.append(li);
					strB.append("</root>\n");
				} else {
					String li = word + "\t" + lemma + "\t" + tag + "\t"
							+ depIndex + "\t" + headWord + "\t" + headIndex
							+ "\t" + rel + direction + "\t" + hTag + "\n";
					strB.append(li);
				}
				if (word.equals(lastNPWord)) {
					strB.append("</NP>\n");
					NPFlag = false;
					i++;
				}
			} else {
				if (hypers.contains(word)) {
					hTag = "hyper";
				} else if (hypos.contains(word)) {
					hTag = "hypo";
				}
				String li = word + "\t" + lemma + "\t" + tag + "\t" + depIndex
						+ "\t" + headWord + "\t" + headIndex + "\t" + rel
						+ direction + "\t" + hTag + "\n";
				strB.append(li);
			}
		}
		return strB.append("</s>\n");
	}

	public String removeAnnotation(String sentence) {
		return sentence.replace("_hyper", "").replace("_hypo", "")
				.replace("_", " ");
	}

	public void corpusPreprocess(String corpusPath, String outputFile,
			boolean withAnnotation) {
		BufferedWriter bw = null;
		FileOutputStream ofsrteam2 = null;
		try {
			ofsrteam2 = new FileOutputStream(outputFile);
		} catch (FileNotFoundException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		bw = new BufferedWriter(new OutputStreamWriter(ofsrteam2));
		try {
			bw.write("<Text>\n");
		} catch (IOException e1) {
			// TODO Auto-generated catch block
			e1.printStackTrace();
		}
		try (BufferedReader br = new BufferedReader(new FileReader(corpusPath))) {
			String sentence;
			int i = 0;
			while ((sentence = br.readLine()) != null) {
				System.out.println(i++);
				if (!withAnnotation)
					sentence = removeAnnotation(sentence);
				bw.write(sentenceParsing(sentence).toString());
			}
		} catch (Exception e) {
			// TODO: handle exception
			System.out.println(e.toString());
		} finally {
			try {
				bw.write("</Text>");
				bw.close();
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}
	}

	public static void main(String[] args) {
		CorpusPreprocessing cp = new CorpusPreprocessing();
		// use true if sentences are annotated by hyponyms and hypernyms
		// otherwise false
		boolean withAnnotation = false;
		// path of semantically positive sentences and the path to save the
		// result.
		String posCorpusPath = "E:\\ProposalPythonCode\\HypRelExtApps\\labeled_corpus\\Music_Sem_Pos.txt";
		String posOutputFile = "E:\\ProposalPythonCode\\HypRelExtApps\\processed_corpus\\Music_Sem_Pos_processed.txt";
		cp.corpusPreprocess(posCorpusPath, posOutputFile, withAnnotation);
		// path of semantically positive sentences and the path to save the
		// result.
		String negCorpusPath = "E:\\ProposalPythonCode\\HypRelExtApps\\labeled_corpus\\Music_Neg_Samples.txt";
		String negOutputFile = "E:\\ProposalPythonCode\\HypRelExtApps\\processed_corpus\\Music_Neg_Samples_processed.txt";
		cp.corpusPreprocess(negCorpusPath, negOutputFile, withAnnotation);
	}
}
